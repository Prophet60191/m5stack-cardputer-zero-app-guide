// SPDX-License-Identifier: MIT
#pragma once

#include "lvgl.h"

namespace cp0_ui {

// Fixed positions for the NFC-style 320x170 menu. These layout helpers do not
// own LVGL objects, interpret keys, or require a subtitle or footer.
struct CarouselLayout {
    static constexpr int screen_width = 320, screen_height = 170;
    static constexpr int center_x = 52, center_y = 32;
    static constexpr int center_width = 216, center_height = 105;
    static constexpr int center_icon_y = 33, center_icon_px = 40;
    static constexpr int title_y = 82, dots_y = 138;
    static constexpr int left_icon_x = 14, right_icon_x = 270;
    static constexpr int side_icon_y = 69, side_icon_width = 37, side_icon_px = 28;

    // body_top is the screen y-coordinate of the shared parent.
    static void place_side_icon(lv_obj_t* icon, bool right, int body_top) {
        lv_obj_set_pos(icon, right ? right_icon_x : left_icon_x, side_icon_y - body_top);
        lv_obj_set_width(icon, side_icon_width);
        lv_obj_set_style_text_align(icon, LV_TEXT_ALIGN_LEFT, 0);
    }
    static void place_center(lv_obj_t* group, int body_top) {
        lv_obj_set_pos(group, center_x, center_y - body_top);
        lv_obj_set_size(group, center_width, center_height);
    }
    static void place_center_icon(lv_obj_t* icon) {
        place_centered_label(icon, center_icon_y);
    }
    static void place_title(lv_obj_t* title) {
        place_centered_label(title, title_y);
    }

private:
    static void place_centered_label(lv_obj_t* item, int screen_y) {
        lv_obj_set_pos(item, 0, screen_y - center_y);
        lv_obj_set_width(item, center_width);
        lv_obj_set_style_text_align(item, LV_TEXT_ALIGN_CENTER, 0);
    }
};

} // namespace cp0_ui
