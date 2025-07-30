#! /usr/bin/env bash

function test_bluer_algo_image_classifier_ingest() {
    local options=$1

    local object_name=test_bluer_algo_image_classifier_ingest-$(bluer_ai_string_timestamp)

    bluer_ai_eval ,$options \
        bluer_algo_image_classifier_ingest \
        clone,count=10 \
        $object_name
}
