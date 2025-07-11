/**
 * @file lv_conf.h
 * Configuration file for LVGL v9.2.x
 */

#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

/*====================
   MEMORY SETTINGS
 *====================*/

/* Size of the memory available for `lv_malloc()` in bytes (>= 2kB) */
#define LV_MEM_SIZE (64 * 1024U)          /* [bytes] */

/* Set an address for the memory pool instead of allocating it as a normal array. Can be in external SRAM too. */
#define LV_MEM_ADR 0     /* 0: allocate automatically, LV_MEM_ADR: set an address */

/* Instead of an address give a memory allocator that will be called to get a memory pool for LVGL. E.g. my_malloc */
#if LV_MEM_ADR == 0
    #define LV_MEM_POOL_INCLUDE <stdlib.h>      /* Uncomment if using an external allocator*/
    #define LV_MEM_POOL_ALLOC   malloc          /* Uncomment if using an external allocator*/
#endif

/*====================
   HAL SETTINGS
 *====================*/

/* Default display refresh, input device read and animation step period. */
#define LV_DEF_REFR_PERIOD  16      /* [ms] */

/* Input device read period in milliseconds */
#define LV_INDEV_DEF_READ_PERIOD 30     /* [ms] */

/* Use a custom tick source that tells the elapsed time in milliseconds.
 * It removes the need to manually update the tick with `lv_tick_inc()`) */
#define LV_TICK_CUSTOM 1
#if LV_TICK_CUSTOM
    #define LV_TICK_CUSTOM_INCLUDE "Arduino.h"         /* Header for the system time function */
    #define LV_TICK_CUSTOM_SYS_TIME_EXPR (millis())    /* Expression evaluating to current system time in ms */
#endif   /* LV_TICK_CUSTOM */

/* Default Dot Per Inch. Used to initialize default sizes such as widgets sized, style paddings.
 * (Not so important, you can adjust it to modify default sizes and spaces) */
#define LV_DPI_DEF 130     /* [px/inch] */

/*====================
 * FEATURE CONFIGURATION
 *====================*/

/* Drawing */
#define LV_DRAW_SW 1

/* Enable complex draw engine.
 * Required to draw shadow, gradient, rounded corners, circles, arc, skew, image transformations or any masks */
#define LV_DRAW_SW_COMPLEX 1

/* Default image cache size. Image caching keeps the images opened.
 * If only the built-in image formats are used there is no real advantage of caching. */
#define LV_IMG_CACHE_DEF_SIZE 0

/* Number of stops allowed per gradient. Increase this to allow more stops per gradient. */
#define LV_GRADIENT_MAX_STOPS 2

/* Default gradient buffer size.
 * When LVGL calculates the gradient "maps" it can save them into a cache to avoid calculating them again.
 * LV_GRAD_CACHE_DEF_SIZE sets the size of this cache in bytes. */
#define LV_GRAD_CACHE_DEF_SIZE 0

/* Allow dithering the gradients (to achieve visual smooth color gradients on limited color depth display) */
#define LV_DITHER_GRADIENT 0

/* Add support for error diffusion dithering.
 * Error diffusion dithering gets a much better visual result, but implies more CPU consumption and memory when drawing.
 * The increase in memory consumption is (32 bits * object width) plus 24 bits * object width if using black/white dithering */
#define LV_DITHER_ERROR_DIFFUSION 0

/* Maximum buffer size to allocate for rotation.
 * Only used if software rotation is enabled in the display driver. */
#define LV_DISP_ROT_MAX_BUF (10*1024)

/*====================
 *   LOGGING
 *====================*/

/* Enable the log module */
#define LV_USE_LOG 0
#if LV_USE_LOG

    /* How important log should be added:
     * LV_LOG_LEVEL_TRACE       A lot of logs to give detailed information
     * LV_LOG_LEVEL_INFO        Log important events
     * LV_LOG_LEVEL_WARN        Log if something unwanted happened but didn't cause a problem
     * LV_LOG_LEVEL_ERROR       Only critical issue, when the system may fail
     * LV_LOG_LEVEL_USER        Only logs added by the user
     * LV_LOG_LEVEL_NONE        Do not log anything */
    #define LV_LOG_LEVEL LV_LOG_LEVEL_WARN

    /* 1: Print the log with 'printf';
     * 0: User need to register a callback with `lv_log_register_print_cb()` */
    #define LV_LOG_PRINTF 0

    /* Enable/disable LV_LOG_TRACE in modules that produces a huge number of logs */
    #define LV_LOG_TRACE_MEM        1
    #define LV_LOG_TRACE_TIMER      1
    #define LV_LOG_TRACE_INDEV      1
    #define LV_LOG_TRACE_DISP_REFR  1
    #define LV_LOG_TRACE_EVENT      1
    #define LV_LOG_TRACE_OBJ_CREATE 1
    #define LV_LOG_TRACE_LAYOUT     1
    #define LV_LOG_TRACE_ANIM       1

#endif  /* LV_USE_LOG */

/*====================
 *   WIDGETS
 *====================*/

/* Documentation of the widgets: https://docs.lvgl.io/latest/en/widgets/index.html */

#define LV_USE_LABEL    1
#define LV_USE_BTN      1

#if LV_USE_BTN
    #define LV_USE_BTNMATRIX    1
#endif

#define LV_USE_CHECKBOX     0
#define LV_USE_DROPDOWN     1
#define LV_USE_IMG          0
#define LV_USE_LINE         0
#define LV_USE_ROLLER       0
#define LV_USE_SLIDER       0
#define LV_USE_SWITCH       0
#define LV_USE_TEXTAREA     1
#define LV_USE_TABLE        0

/*====================
 *   EXAMPLES
 *====================*/

/* Enable the examples to be built with the library */
#define LV_BUILD_EXAMPLES 0

/*====================
 *    THEME USAGE
 *====================*/

/* A simple, impressive and very complete theme */
#define LV_USE_THEME_DEFAULT 1
#if LV_USE_THEME_DEFAULT

    /* 0: Light mode; 1: Dark mode */
    #define LV_THEME_DEFAULT_DARK 1

    /* 1: Enable grow on press */
    #define LV_THEME_DEFAULT_GROW 1

    /* Default transition time in [ms] */
    #define LV_THEME_DEFAULT_TRANSITION_TIME 80
#endif /* LV_USE_THEME_DEFAULT */

/* A very simple theme that is a good starting point for a custom theme */
#define LV_USE_THEME_BASIC 0

/* A theme designed for monochrome displays */
#define LV_USE_THEME_MONO 0

/*====================
 *    FONTS
 *====================*/

/* Montserrat fonts with various styles and sizes for a modern look */
#define LV_FONT_MONTSERRAT_8  0
#define LV_FONT_MONTSERRAT_10 0
#define LV_FONT_MONTSERRAT_12 0
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_MONTSERRAT_16 1
#define LV_FONT_MONTSERRAT_18 0
#define LV_FONT_MONTSERRAT_20 0
#define LV_FONT_MONTSERRAT_22 0
#define LV_FONT_MONTSERRAT_24 0
#define LV_FONT_MONTSERRAT_26 0
#define LV_FONT_MONTSERRAT_28 0
#define LV_FONT_MONTSERRAT_30 0
#define LV_FONT_MONTSERRAT_32 0
#define LV_FONT_MONTSERRAT_34 0
#define LV_FONT_MONTSERRAT_36 0
#define LV_FONT_MONTSERRAT_38 0
#define LV_FONT_MONTSERRAT_40 0
#define LV_FONT_MONTSERRAT_42 0
#define LV_FONT_MONTSERRAT_44 0
#define LV_FONT_MONTSERRAT_46 0
#define LV_FONT_MONTSERRAT_48 0

/* Demonstrate special features */
#define LV_FONT_MONTSERRAT_12_SUBPX      0
#define LV_FONT_MONTSERRAT_28_COMPRESSED 0  /* bpp = 3 */
#define LV_FONT_DEJAVU_16_PERSIAN_HEBREW 0  /* Hebrew, Arabic, Perisan letters and all their forms */
#define LV_FONT_SIMSUN_16_CJK            0  /* 1000 most common CJK radicals */

/* Pixel perfect monospace fonts */
#define LV_FONT_UNSCII_8  0
#define LV_FONT_UNSCII_16 0

/* Optionally declare custom fonts here.
 * You can use these fonts as default font too and they will be available globally.
 * E.g. #define LV_FONT_CUSTOM_DECLARE   LV_FONT_DECLARE(my_font_1) LV_FONT_DECLARE(my_font_2) */
#define LV_FONT_CUSTOM_DECLARE

/* Always set a default font */
#define LV_FONT_DEFAULT &lv_font_montserrat_14

/*====================
 *   TEXT SETTINGS
 *====================*/

/**
 * Select a character encoding for strings.
 * Your IDE or editor should have the same character encoding
 * - LV_TXT_ENC_UTF8
 * - LV_TXT_ENC_ASCII
 */
#define LV_TXT_ENC LV_TXT_ENC_UTF8

/* Can break (wrap) texts on these chars */
#define LV_TXT_BREAK_CHARS " ,.;:-_"

/* If a word is at least this long, will break wherever "prettiest"
 * To disable, set to a value <= 0 */
#define LV_TXT_LINE_BREAK_LONG_LEN 0

/* Minimum number of characters in a long word to put on a line before a break.
 * Depends on LV_TXT_LINE_BREAK_LONG_LEN. */
#define LV_TXT_LINE_BREAK_LONG_PRE_MIN_LEN 3

/* Minimum number of characters in a long word to put on a line after a break.
 * Depends on LV_TXT_LINE_BREAK_LONG_LEN. */
#define LV_TXT_LINE_BREAK_LONG_POST_MIN_LEN 3

/* Support bidirectional texts. Allows mixing Left-to-Right and Right-to-Left texts.
 * The direction will be processed according to the Unicode Bidirectional Algorithm:
 * https://www.unicode.org/reports/tr9/*/
#define LV_USE_BIDI 0
#if LV_USE_BIDI
    /* Set the default direction. Supported values:
     * `LV_BASE_DIR_LTR` Left-to-Right
     * `LV_BASE_DIR_RTL` Right-to-Left
     * `LV_BASE_DIR_AUTO` detect texts base direction */
    #define LV_BIDI_BASE_DIR_DEF LV_BASE_DIR_AUTO
#endif

/* Enable Arabic/Persian processing
 * In these languages characters should be replaced with an other form based on their position in the text */
#define LV_USE_ARABIC_PERSIAN_CHARS 0

/*====================
 *   WIDGET USAGE
 *====================*/

/* Documentation of the widgets: https://docs.lvgl.io/latest/en/widgets/index.html */

#define LV_USE_ANIMIMG 0

#define LV_USE_ARC 0

#define LV_USE_BAR 0

#define LV_USE_BTN 1

#define LV_USE_BTNMATRIX 1

#define LV_USE_CANVAS 0

#define LV_USE_CHECKBOX 0

#define LV_USE_DROPDOWN 0

#define LV_USE_IMG 0

#define LV_USE_LABEL 1
#if LV_USE_LABEL
    #define LV_LABEL_TEXT_SELECTION 0   /* Enable selecting text of the label */
    #define LV_LABEL_LONG_TXT_HINT 0    /* Store some extra info in labels to speed up drawing of very long texts */
    #define LV_LABEL_WAIT_CHAR_COUNT 3  /* The count of wait characters */
#endif

#define LV_USE_LINE 0

#define LV_USE_LIST 0

#define LV_USE_MENU 0

#define LV_USE_METER 0

#define LV_USE_MSGBOX 0

#define LV_USE_ROLLER 0

#define LV_USE_SLIDER 0

#define LV_USE_SPAN 0

#define LV_USE_SPINBOX 0

#define LV_USE_SPINNER 0

#define LV_USE_SWITCH 0

#define LV_USE_TABLE 0

#define LV_USE_TABVIEW 0

#define LV_USE_TEXTAREA 0

#define LV_USE_TILEVIEW 0

#define LV_USE_WIN 0

/*==================
 * EXTRA COMPONENTS
 *==================*/

/* 1: Enable the extra "layouts" */
#define LV_USE_FLEX 1
#define LV_USE_GRID 0

/*==================
 * OTHERS
 *==================*/

/* 1: Enable API to take snapshot for object */
#define LV_USE_SNAPSHOT 0

/* 1: Enable Monkey test */
#define LV_USE_MONKEY 0

/* 1: Enable grid navigation */
#define LV_USE_GRIDNAV 0

/* 1: Enable lv_obj fragment */
#define LV_USE_FRAGMENT 0

/* 1: Support using images as font in label or span widgets */
#define LV_USE_IMGFONT 0

/* 1: Enable a published subscriber based messaging system */
#define LV_USE_MSG 0

/* 1: Enable Pinyin input method */
/* Requires: lv_keyboard */
#define LV_USE_IME_PINYIN 0

/* 1: Enable file explorer */
/* Requires: lv_table */
#define LV_USE_FILE_EXPLORER 0

/*==================
 * DEVICE DRIVERS
 *==================*/

/* Use SDL to open a window on PC and handle mouse and keyboard */
#define LV_USE_SDL 0

/* Driver for /dev/fb* */
#define LV_USE_LINUX_FBDEV 0

/* Driver for /dev/dri/card* */
#define LV_USE_LINUX_DRM 0

/* Use libevdev for input device handling */
#define LV_USE_LIBEVDEV 0

/* Use XKB for keyboard layouts */
#define LV_USE_XKB 0

/* Use libudev for input device hot plugging */
#define LV_USE_LIBUDEV 0

/*==================
 * EXAMPLES
 *==================*/

/* Enable the examples to be built with the library */
#define LV_BUILD_EXAMPLES 0

/*==================
 * DOCUMENTATION
 *==================*/

/* Show some widget. It might be required to increase `LV_MEM_SIZE` */
#define LV_USE_DEMO_WIDGETS 0
#if LV_USE_DEMO_WIDGETS
    #define LV_DEMO_WIDGETS_SLIDESHOW 0
#endif

/* Demonstrate the usage of encoder and keyboard */
#define LV_USE_DEMO_KEYPAD_AND_ENCODER 0

/* Benchmark your system */
#define LV_USE_DEMO_BENCHMARK 0

/* Render test for the library */
#define LV_USE_DEMO_RENDER 0

/* Stress test for the system */
#define LV_USE_DEMO_STRESS 0

/* Music player demo */
#define LV_USE_DEMO_MUSIC 0
#if LV_USE_DEMO_MUSIC
    #define LV_DEMO_MUSIC_SQUARE    0
    #define LV_DEMO_MUSIC_LANDSCAPE 0
    #define LV_DEMO_MUSIC_ROUND     0
    #define LV_DEMO_MUSIC_LARGE     0
    #define LV_DEMO_MUSIC_AUTO_PLAY 0
#endif

/* Flex layout demo */
#define LV_USE_DEMO_FLEX_LAYOUT 0

/* Smart-phone like multi-language demo */
#define LV_USE_DEMO_MULTILANG 0

/* Widget transformation demo */
#define LV_USE_DEMO_TRANSFORM 0

/* Demonstrate scroll settings */
#define LV_USE_DEMO_SCROLL 0

/* Vector graphic demo */
#define LV_USE_DEMO_VECTOR_GRAPHIC 0

#endif /*LV_CONF_H*/