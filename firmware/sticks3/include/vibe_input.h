#pragma once

#include <stdbool.h>

static inline bool vibe_input_should_wake_only(bool display_awake)
{
    return !display_awake;
}
