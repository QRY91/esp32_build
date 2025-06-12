#include <furi.h>
#include <gui/gui.h>
#include <input/input.h>
#include <stdlib.h>
#include <furi_hal_random.h>

// Custom logo bitmap (8x8)
static const uint8_t logo_bitmap[] = {
    0b11111111,  // Row 0
    0b10000001,  // Row 1
    0b10111101,  // Row 2
    0b10111101,  // Row 3
    0b10111111,  // Row 4
    0b10111001,  // Row 5
    0b10001001,  // Row 6
    0b11111111   // Row 7
};

// Glyph type enumeration
typedef enum {
    GLYPH_TYPE_DICE,
    GLYPH_TYPE_CARD,
    GLYPH_TYPE_ROMAN,
    GLYPH_TYPE_CUSTOM,
} GlyphType;

// Core glyph structure
typedef struct {
    GlyphType type;
    const char* name;
    int value;
    const char* display_symbol;
} Glyph;

// Standard 6-sided dice glyphs + quantum face (7-sided total)
static const Glyph dice_glyphs[] = {
    {GLYPH_TYPE_DICE, "one", 1, "1"},
    {GLYPH_TYPE_DICE, "two", 2, "2"},
    {GLYPH_TYPE_DICE, "three", 3, "3"},
    {GLYPH_TYPE_DICE, "four", 4, "4"},
    {GLYPH_TYPE_DICE, "five", 5, "5"},
    {GLYPH_TYPE_DICE, "six", 6, "6"},
    {GLYPH_TYPE_CUSTOM, "quantum", 0, "?"},
};

// All possible unlockable quantum glyphs
static const Glyph all_quantum_glyphs[] = {
    // Card glyphs
    {GLYPH_TYPE_CARD, "jack", 11, "J"},
    {GLYPH_TYPE_CARD, "queen", 13, "Q"},
    {GLYPH_TYPE_CARD, "king", 13, "K"},
    {GLYPH_TYPE_CARD, "ace", 14, "A"},
    // Roman numeral glyphs
    {GLYPH_TYPE_ROMAN, "I", 1, "I"},
    {GLYPH_TYPE_ROMAN, "V", 5, "V"},
    {GLYPH_TYPE_ROMAN, "X", 10, "X"},
    {GLYPH_TYPE_ROMAN, "L", 50, "L"},
    {GLYPH_TYPE_ROMAN, "C", 100, "C"},
};

// Unlocked quantum glyphs (grows during gameplay)
static Glyph quantum_glyphs[10]; // Max 10 unlocked glyphs
static size_t quantum_glyph_count = 0;

// Roll table structure
typedef struct {
    const Glyph* glyphs;
    size_t count;
    const char* table_name;
} RollTable;

// Available roll tables
static const RollTable roll_tables[] = {
    {dice_glyphs, sizeof(dice_glyphs) / sizeof(dice_glyphs[0]), "Quantum Die"},
};

// Game screen states
typedef enum {
    SCREEN_SPLASH,    // Startup splash screen
    SCREEN_GAME,      // Main gameplay
    SCREEN_HELP,      // Help/controls screen
} ScreenState;

// App state structure
typedef struct {
    Gui* gui;
    ViewPort* view_port;
    FuriMessageQueue* event_queue;

    // Game state
    int current_table_index;
    const Glyph* last_roll;
    int roll_count;
    int total_score;
    bool show_stats;
    int target_score;
    int max_rolls;
    bool game_won;
    bool game_over;

    // Quantum state
    bool is_quantum_roll;
    int unlocked_glyphs;

    // UI state
    ScreenState current_screen;
    bool show_controls;
    uint32_t splash_timer;
    uint32_t result_delay;

    // Animation state
    bool is_rolling;
    uint32_t roll_animation_frame;
} QuantumDiceApp;

// RNG function using Flipper's random
static const Glyph* roll_glyph(QuantumDiceApp* app, const RollTable* table) {
    if(table->count == 0) return NULL;

    uint32_t random_index = furi_hal_random_get() % table->count;
    const Glyph* rolled_glyph = &table->glyphs[random_index];

    // Check if quantum face was rolled
    if(rolled_glyph->type == GLYPH_TYPE_CUSTOM && rolled_glyph->value == 0) {
        app->is_quantum_roll = true;

        // Check if we have unlocked quantum glyphs
        if(quantum_glyph_count > 0) {
            // Roll from the quantum pool
            uint32_t quantum_index = furi_hal_random_get() % quantum_glyph_count;
            return &quantum_glyphs[quantum_index];
        }

        // No quantum glyphs unlocked, reroll as regular die
        uint32_t reroll_index = furi_hal_random_get() % 6; // Only first 6 faces
        return &table->glyphs[reroll_index];
    }

    return rolled_glyph;
}

// Draw custom logo bitmap
static void draw_logo(Canvas* canvas, int x, int y, int scale) {
    for(int row = 0; row < 8; row++) {
        for(int col = 0; col < 8; col++) {
            if(logo_bitmap[row] & (1 << (7 - col))) {
                // Draw scaled pixel
                for(int sy = 0; sy < scale; sy++) {
                    for(int sx = 0; sx < scale; sx++) {
                        canvas_draw_dot(canvas, x + col * scale + sx, y + row * scale + sy);
                    }
                }
            }
        }
    }
}

// Full width splash screen
static void draw_splash_screen(Canvas* canvas, QuantumDiceApp* app) {
    UNUSED(app);

    // Title
    canvas_set_font(canvas, FontPrimary);
    canvas_draw_str_aligned(canvas, 64, 8, AlignCenter, AlignTop, "Quantum Dice");

    // Custom logo (8x8 scaled 3x = 24x24)
    draw_logo(canvas, 52, 25, 3);

    // Version and credits
    canvas_set_font(canvas, FontSecondary);
    canvas_draw_str_aligned(canvas, 64, 58, AlignCenter, AlignTop, "Press Any Button");
}

// Full width game screen
static void draw_game_screen(Canvas* canvas, QuantumDiceApp* app) {
    // Game status - combined on one line
    canvas_set_font(canvas, FontSecondary);
    char status_text[64];
    snprintf(status_text, sizeof(status_text), "Score: %d/%d  Rolls: %d/%d",
             app->total_score, app->target_score, app->roll_count, app->max_rolls);
    canvas_draw_str_aligned(canvas, 64, 8, AlignCenter, AlignTop, status_text);

    // Main roll display area - don't show if game over message should be displayed
    if(app->is_rolling) {
        // Rolling animation
        canvas_set_font(canvas, FontPrimary);
        const char* rolling_frames[] = {"Rolling.", "Rolling..", "Rolling..."};
        int frame_index = (app->roll_animation_frame / 5) % 3;
        canvas_draw_str_aligned(canvas, 64, 35, AlignCenter, AlignCenter, rolling_frames[frame_index]);
    } else if(app->last_roll &&
             !((app->total_score >= app->target_score || app->roll_count >= app->max_rolls) && app->result_delay == 0)) {
        // Display the rolled glyph (but not if showing win/game over)
        canvas_set_font(canvas, FontBigNumbers);
        canvas_draw_str_aligned(canvas, 64, 35, AlignCenter, AlignCenter, app->last_roll->display_symbol);

        // Display glyph info
        canvas_set_font(canvas, FontSecondary);
        char glyph_info[32];
        if(app->is_quantum_roll) {
            snprintf(glyph_info, sizeof(glyph_info), "Quantum! %d pts",
                    app->last_roll->value);
        } else {
            snprintf(glyph_info, sizeof(glyph_info), "%s: %d pts",
                    app->last_roll->name, app->last_roll->value);
        }
        canvas_draw_str_aligned(canvas, 64, 48, AlignCenter, AlignTop, glyph_info);
    } else if(!app->last_roll) {
        // Initial state
        canvas_set_font(canvas, FontSecondary);
        canvas_draw_str_aligned(canvas, 64, 35, AlignCenter, AlignCenter, "Press OK to roll!");
    }

    // Game over conditions (don't show roll result when displaying end states)
    if(app->total_score >= app->target_score && app->result_delay == 0) {
        canvas_set_font(canvas, FontPrimary);
        canvas_draw_str_aligned(canvas, 64, 30, AlignCenter, AlignTop, "YOU WIN!");
        canvas_set_font(canvas, FontSecondary);
        canvas_draw_str_aligned(canvas, 64, 42, AlignCenter, AlignTop, "Up: Next Level");
    } else if(app->roll_count >= app->max_rolls && app->result_delay == 0) {
        canvas_set_font(canvas, FontPrimary);
        canvas_draw_str_aligned(canvas, 64, 30, AlignCenter, AlignTop, "Game Over");
        canvas_set_font(canvas, FontSecondary);
        canvas_draw_str_aligned(canvas, 64, 42, AlignCenter, AlignTop, "Down: Restart");
    }

    // Stats section
    if(app->show_stats && app->roll_count > 0) {
        canvas_set_font(canvas, FontSecondary);
        char stats_text1[32];
        char stats_text2[32];
        snprintf(stats_text1, sizeof(stats_text1), "Total: %d pts", app->total_score);
        snprintf(stats_text2, sizeof(stats_text2), "Avg: %.1f per roll",
                (double)app->total_score / app->roll_count);
        canvas_draw_str_aligned(canvas, 64, 52, AlignCenter, AlignTop, stats_text1);
        canvas_draw_str_aligned(canvas, 64, 62, AlignCenter, AlignTop, stats_text2);
    }

    // Show minimal controls or hint if enabled
    if(app->show_controls) {
        canvas_set_font(canvas, FontSecondary);
        canvas_draw_str_aligned(canvas, 64, 60, AlignCenter, AlignBottom, "R: Help");
    }
}

// Full width help screen
static void draw_help_screen(Canvas* canvas) {
    canvas_set_font(canvas, FontPrimary);
    canvas_draw_str_aligned(canvas, 64, 7, AlignCenter, AlignTop, "Controls");
    
    canvas_set_font(canvas, FontSecondary);
    canvas_draw_str_aligned(canvas, 64, 20, AlignCenter, AlignTop, "OK: Roll dice");
    canvas_draw_str_aligned(canvas, 64, 28, AlignCenter, AlignTop, "Right: Help");
    canvas_draw_str_aligned(canvas, 64, 36, AlignCenter, AlignTop, "Left: Stats");
    canvas_draw_str_aligned(canvas, 64, 44, AlignCenter, AlignTop, "Up: Next level");
    canvas_draw_str_aligned(canvas, 64, 52, AlignCenter, AlignTop, "Down: Restart");
    
    canvas_draw_str_aligned(canvas, 64, 60, AlignCenter, AlignBottom, "Any button: Back");
}

// Draw function
static void quantum_dice_draw_callback(Canvas* canvas, void* ctx) {
    QuantumDiceApp* app = ctx;

    canvas_clear(canvas);
    canvas_set_color(canvas, ColorBlack);

    // Draw different screens based on state
    switch(app->current_screen) {
        case SCREEN_SPLASH:
            draw_splash_screen(canvas, app);
            break;
        case SCREEN_GAME:
            draw_game_screen(canvas, app);
            break;
        case SCREEN_HELP:
            draw_help_screen(canvas);
            break;
    }
}

// Input callback
static void quantum_dice_input_callback(InputEvent* input_event, void* ctx) {
    furi_assert(ctx);
    QuantumDiceApp* app = ctx;

    furi_message_queue_put(app->event_queue, input_event, FuriWaitForever);
}

// Process splash screen input
static bool process_splash_input(QuantumDiceApp* app, InputEvent event) {
    if(event.type == InputTypePress) {
        // Any button press exits splash screen
        app->current_screen = SCREEN_GAME;
        app->show_controls = true; // Show controls hint initially
        return true;
    }

    // Check if splash timer expired
    if(app->splash_timer > 0) {
        app->splash_timer--;
        if(app->splash_timer == 0) {
            app->current_screen = SCREEN_GAME;
            app->show_controls = true;
            return true;
        }
    }

    return false;
}

// Process help screen input
static bool process_help_input(QuantumDiceApp* app, InputEvent event) {
    if(event.type == InputTypePress) {
        // Any button press exits help screen
        app->current_screen = SCREEN_GAME;
        return true;
    }
    return false;
}

// Handle roll action
static void perform_roll(QuantumDiceApp* app) {
    if(app->is_rolling || app->roll_count >= app->max_rolls) return;
    if(app->total_score >= app->target_score) return; // Game already won

    app->is_rolling = true;
    app->is_quantum_roll = false;
    app->roll_animation_frame = 0;
    app->game_won = false;
    app->game_over = false;

    // Simulate roll delay with animation
    for(int i = 0; i < 20; i++) {
        app->roll_animation_frame++;
        view_port_update(app->view_port);
        furi_delay_ms(50); // 50ms * 20 = 1 second roll animation
    }

    // Perform the actual roll
    const RollTable* current_table = &roll_tables[app->current_table_index];
    app->last_roll = roll_glyph(app, current_table);

    if(app->last_roll) {
        app->roll_count++;
        app->total_score += app->last_roll->value;

        // Set delay before showing game result
        app->result_delay = 20; // ~2 seconds to see the roll result

        // Check for level completion
        if(app->total_score >= app->target_score) {
            app->game_won = true;

            // Unlock a new quantum glyph as reward
            if(app->unlocked_glyphs < (int)(sizeof(all_quantum_glyphs)/sizeof(all_quantum_glyphs[0]))) {
                // Add a new glyph to the quantum pool
                if(quantum_glyph_count < 10) { // Prevent overflow
                    quantum_glyphs[quantum_glyph_count] = all_quantum_glyphs[app->unlocked_glyphs];
                    quantum_glyph_count++;
                    app->unlocked_glyphs++;
                }
            }
        } else if(app->roll_count >= app->max_rolls) {
            app->game_over = true;
        }
    }

    app->is_rolling = false;
}

// Start new level
static void start_new_level(QuantumDiceApp* app) {
    app->target_score += 15; // Increase difficulty
    app->max_rolls = 6; // Reset rolls
    app->roll_count = 0;
    app->total_score = 0;
    app->game_won = false;
    app->game_over = false;
    app->last_roll = NULL;
    app->result_delay = 0;
}

// Restart game
static void restart_game(QuantumDiceApp* app) {
    app->target_score = 21; // Starting target
    app->max_rolls = 6;
    app->roll_count = 0;
    app->total_score = 0;
    app->game_won = false;
    app->game_over = false;
    app->last_roll = NULL;
    app->unlocked_glyphs = 0;
    app->result_delay = 0;
    // Reset quantum glyphs pool
    quantum_glyph_count = 0;
}

// App allocation
static QuantumDiceApp* quantum_dice_app_alloc() {
    QuantumDiceApp* app = malloc(sizeof(QuantumDiceApp));

    app->event_queue = furi_message_queue_alloc(8, sizeof(InputEvent));

    app->view_port = view_port_alloc();
    view_port_draw_callback_set(app->view_port, quantum_dice_draw_callback, app);
    view_port_input_callback_set(app->view_port, quantum_dice_input_callback, app);

    app->gui = furi_record_open(RECORD_GUI);
    gui_add_view_port(app->gui, app->view_port, GuiLayerFullscreen);

    // Initialize game state
    app->current_table_index = 0;
    app->last_roll = NULL;
    app->roll_count = 0;
    app->total_score = 0;
    app->show_stats = false;
    app->target_score = 21; // Starting target score
    app->max_rolls = 6; // Starting max rolls
    app->game_won = false;
    app->game_over = false;

    // Initialize quantum state
    app->is_quantum_roll = false;
    app->unlocked_glyphs = 0;

    // Initialize UI state
    app->current_screen = SCREEN_SPLASH;
    app->show_controls = false;
    app->splash_timer = 50; // ~5 seconds splash screen (50 * 100ms loop)
    app->result_delay = 0;

    // Initialize animation state
    app->is_rolling = false;
    app->roll_animation_frame = 0;

    return app;
}

// App cleanup
static void quantum_dice_app_free(QuantumDiceApp* app) {
    furi_assert(app);

    gui_remove_view_port(app->gui, app->view_port);
    view_port_free(app->view_port);
    furi_record_close(RECORD_GUI);

    furi_message_queue_free(app->event_queue);

    free(app);
}

// Main app entry point
int32_t quantum_dice_app(void* p) {
    UNUSED(p);

    QuantumDiceApp* app = quantum_dice_app_alloc();

    InputEvent event;
    bool running = true;
    bool event_handled = false;

    while(running) {
        if(furi_message_queue_get(app->event_queue, &event, 100) == FuriStatusOk) {
            event_handled = false;

            // Process input based on current screen
            switch(app->current_screen) {
                case SCREEN_SPLASH:
                    event_handled = process_splash_input(app, event);
                    break;

                case SCREEN_HELP:
                    event_handled = process_help_input(app, event);
                    break;

                case SCREEN_GAME:
                    if(event.type == InputTypePress) {
                        switch(event.key) {
                            case InputKeyBack:
                                running = false;
                                event_handled = true;
                                break;

                            case InputKeyOk:
                                if(!app->is_rolling) {
                                    perform_roll(app);
                                    app->show_controls = false; // Hide controls after first roll
                                    event_handled = true;
                                }
                                break;

                            case InputKeyRight:
                                app->current_screen = SCREEN_HELP;
                                event_handled = true;
                                break;

                            case InputKeyLeft:
                                app->show_stats = !app->show_stats;
                                event_handled = true;
                                break;

                            case InputKeyUp:
                                if(app->game_won) {
                                    start_new_level(app);
                                    event_handled = true;
                                }
                                break;

                            case InputKeyDown:
                                if(app->roll_count >= app->max_rolls && app->total_score < app->target_score) {
                                    restart_game(app);
                                    event_handled = true;
                                }
                                break;

                            default:
                                break;
                        }
                    }
                    break;
            }

            if(event_handled) {
                view_port_update(app->view_port);
            }
        } else {
            // No input, update view for animations and timers
            if(app->current_screen == SCREEN_SPLASH && app->splash_timer > 0) {
                app->splash_timer--;
                if(app->splash_timer == 0) {
                    app->current_screen = SCREEN_GAME;
                    app->show_controls = true;
                    view_port_update(app->view_port);
                }
            }

            // Handle result delay timer
            if(app->result_delay > 0) {
                app->result_delay--;
                if(app->result_delay == 0) {
                    // Time to show the result screen
                    view_port_update(app->view_port);
                }
            }
        }
    }

    quantum_dice_app_free(app);

    return 0;
}
