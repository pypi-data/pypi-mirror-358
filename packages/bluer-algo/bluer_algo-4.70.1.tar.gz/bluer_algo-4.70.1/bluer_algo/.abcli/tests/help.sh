#! /usr/bin/env bash

function test_bluer_algo_help() {
    local options=$1

    local module
    for module in \
        "@algo" \
        \
        "@algo pypi" \
        "@algo pypi browse" \
        "@algo pypi build" \
        "@algo pypi install" \
        \
        "@algo pytest" \
        \
        "@algo test" \
        "@algo test list" \
        \
        "@algo image_classifier" \
        "@algo image_classifier ingest" \
        \
        "@image_classifier" \
        "@image_classifier ingest" \
        \
        "bluer_algo"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
