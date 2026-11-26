// SPDX-License-Identifier: MIT
#include "counter_store.h"
#include <cstdlib>
#include <iostream>

void check(bool ok, const char* description) {
    if (!ok) {
        std::cerr << description << '\n';
        std::exit(1);
    }
}

int main(int argc, char** argv) {
    check(argc == 2, "pass a disposable scratch directory");
    const std::filesystem::path scratch(argv[1]);
    const auto count = scratch / "demo" / "count";
    check(model::load_count(count) == 0, "empty state");
    check(model::save_count(count, 3) && model::load_count(count) == 3, "save and reopen");
    check(model::save_count(count, model::kMaxCount), "upper bound");
    check(!model::save_count(count, -1), "negative save");
    check(!model::save_count(count, model::kMaxCount + 1), "out-of-range save");
    check(model::load_count(count) == model::kMaxCount, "failed updates preserve last value");
    check(!std::filesystem::exists(count.string() + ".tmp"), "rename leaves no temp file");
    check(!model::save_count(count / "not-a-directory", 4), "unwritable state path");
    check(model::load_count(count) == model::kMaxCount, "failed write leaves previous file");
    for (std::string invalid : {"99999\n", "-1\n", "hi\n", "2\n3\n", "1x\n"}) {
        std::ofstream(count) << invalid;
        check(model::load_count(count) == 0, "invalid state must load as zero");
    }
    std::ofstream(count).write("3\0x\n", 4);
    check(model::load_count(count) == 0, "reject embedded NUL");
    std::cout << "Counter state tests passed\n";
}
