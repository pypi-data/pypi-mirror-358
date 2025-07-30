#! /usr/bin/env bash

function test_bluer_algo_image_classifier_train() {
    local options=$1

    local model_object_name=test_bluer_algo_image_classifier_train-$(bluer_ai_string_timestamp)

    bluer_ai_eval ,$options \
        bluer_algo_image_classifier_train \
        ,$options \
        fruits-365-dataset-2025-06-28-rtpost \
        $model_object_name
}
