#include <furi.h>
#include <gui/gui.h>
#include <input/input.h>

typedef struct {
    Gui* gui;
    ViewPort* view_port;
    FuriMessageQueue* event_queue;
} QryHelloApp;

static void qry_hello_draw_callback(Canvas* canvas, void* ctx) {
    UNUSED(ctx);
    
    canvas_clear(canvas);
    canvas_set_color(canvas, ColorBlack);
    
    // Header
    canvas_set_font(canvas, FontPrimary);
    canvas_draw_str(canvas, 2, 12, "QRY Labs");
    
    // Subtitle
    canvas_set_font(canvas, FontSecondary);
    canvas_draw_str(canvas, 2, 28, "DeskHog Prototyping");
    
    // Philosophy
    canvas_draw_str(canvas, 2, 42, "Square Peg, Round Hole");
    
    // Instructions
    canvas_draw_str(canvas, 2, 56, "Press Back to exit");
    
    // Footer - systematic approach
    canvas_set_font(canvas, FontKeyboard);
    canvas_draw_str(canvas, 2, 64, "Systematic embedded learning");
}

static void qry_hello_input_callback(InputEvent* input_event, void* ctx) {
    furi_assert(ctx);
    QryHelloApp* app = ctx;
    
    furi_message_queue_put(app->event_queue, input_event, FuriWaitForever);
}

static QryHelloApp* qry_hello_app_alloc() {
    QryHelloApp* app = malloc(sizeof(QryHelloApp));
    
    app->event_queue = furi_message_queue_alloc(8, sizeof(InputEvent));
    
    app->view_port = view_port_alloc();
    view_port_draw_callback_set(app->view_port, qry_hello_draw_callback, app);
    view_port_input_callback_set(app->view_port, qry_hello_input_callback, app);
    
    app->gui = furi_record_open(RECORD_GUI);
    gui_add_view_port(app->gui, app->view_port, GuiLayerFullscreen);
    
    return app;
}

static void qry_hello_app_free(QryHelloApp* app) {
    furi_assert(app);
    
    gui_remove_view_port(app->gui, app->view_port);
    view_port_free(app->view_port);
    furi_record_close(RECORD_GUI);
    
    furi_message_queue_free(app->event_queue);
    
    free(app);
}

int32_t qry_hello_app(void* p) {
    UNUSED(p);
    
    QryHelloApp* app = qry_hello_app_alloc();
    
    InputEvent event;
    bool running = true;
    
    while(running) {
        if(furi_message_queue_get(app->event_queue, &event, 100) == FuriStatusOk) {
            if(event.type == InputTypePress) {
                switch(event.key) {
                case InputKeyBack:
                    running = false;
                    break;
                default:
                    break;
                }
            }
        }
    }
    
    qry_hello_app_free(app);
    
    return 0;
}