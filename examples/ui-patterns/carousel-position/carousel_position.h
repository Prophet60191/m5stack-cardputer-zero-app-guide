// SPDX-License-Identifier: MIT
#pragma once
#include "lvgl.h"
#include <cstddef>
#include <cstdint>
#include <vector>

namespace cp0_ui {
// LVGL owns the container and its children. Drop the handle when its parent is
// rebuilt. This view has no focus, navigation, animation, or app dependencies.
class CarouselPosition {
    std::vector<lv_obj_t*> slots_;
public:
    static constexpr int pitch=9, dot_width=4, selected_width=8, height=3;
    static CarouselPosition create(lv_obj_t* parent, std::size_t count, int y) {
        CarouselPosition result;
        if(count<2||count>24)return result;
        auto* row=lv_obj_create(parent);
        lv_obj_remove_style_all(row);
        lv_obj_clear_flag(row,static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE|LV_OBJ_FLAG_SCROLLABLE|LV_OBJ_FLAG_CLICK_FOCUSABLE));
        lv_obj_set_size(row,static_cast<int>(count)*pitch,height);
        lv_obj_align(row,LV_ALIGN_TOP_MID,0,y);
        result.slots_.reserve(count);
        for(std::size_t i=0;i<count;++i) {
            auto* dot=lv_obj_create(row);
            lv_obj_remove_style_all(dot);
            lv_obj_clear_flag(dot,static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE|LV_OBJ_FLAG_SCROLLABLE|LV_OBJ_FLAG_CLICK_FOCUSABLE));
            lv_obj_set_style_bg_opa(dot,LV_OPA_COVER,0);
            lv_obj_set_style_radius(dot,2,0);
            result.slots_.push_back(dot);
        }
        return result;
    }
    void update(std::size_t active, uint32_t accent, uint32_t muted) {
        for(std::size_t i=0;i<slots_.size();++i) {
            const bool selected=i==active;
            const int width=selected?selected_width:dot_width;
            auto* dot=slots_[i];
            lv_obj_set_size(dot,width,height);
            lv_obj_set_pos(dot,static_cast<int>(i)*pitch+(pitch-width)/2,0);
            lv_obj_set_style_bg_color(dot,lv_color_hex(selected?accent:muted),0);
        }
    }
};
}
