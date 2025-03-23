# Benchmark Results

## Baseline
| Selector                    | Accuracy   |
|-----------------------------|------------|
| WordsMatchingActionSelector | 78.00% |

## Model Results
| Model     | Selector              | Accuracy   | Time Taken (s) |
|-----------|-----------------------|------------|----------------|
| llama3.1  | LLMActionSelector     | 100.00% | 5.69 |
| llama3.1  | LLMActionSelector2    | 62.00% | 25.92 |
| qwen2.5   | LLMActionSelector     | 100.00% | 5.31 |
| qwen2.5   | LLMActionSelector2    | 94.00% | 25.16 |
| gemma3    | LLMActionSelector     | 96.00% | 6.64 |
| gemma3    | LLMActionSelector2    | 78.00% | 40.18 |
| llama3.2  | LLMActionSelector     | 100.00% | 3.18 |
| llama3.2  | LLMActionSelector2    | 16.00% | 19.18 |
| phi4-mini | LLMActionSelector     | 96.00% | 3.93 |
| phi4-mini | LLMActionSelector2    | 76.00% | 25.75 |
| smollm2   | LLMActionSelector     | 88.00% | 2.76 |
| smollm2   | LLMActionSelector2    | 0.00% | 13.14 |

## Detailed Wrong Results
### Model: llama3.1 | Selector: LLMActionSelector2
| User Command | Generated Result |
|--------------|------------------|
| bật sáng | unknown |
| đi tắt đèn | unknown |
| bật quạt | unknown |
| bật quạt đi | unknown |
| mở quạt | unknown |
| bật quạt cho tôi | unknown |
| làm ơn bật quạt | unknown |
| tắt quạt | unknown |
| quạt tắt | unknown |
| hãy tắt quạt | unknown |
| làm ơn tắt quạt | unknown |
| cho tôi tắt quạt | unknown |
| ti vi bật | unknown |
| làm ơn bật ti vi | unknown |
| ti vi tắt | unknown |
| làm ơn bật điều hòa | unknown |
| đi bật điều hòa | unknown |
| đi tắt điều hòa | unknown |
| đi tắt điều hòa đi | unknown |

### Model: qwen2.5 | Selector: LLMActionSelector2
| User Command | Generated Result |
|--------------|------------------|
| tắt quạt | unknown |
| đi tắt điều hòa | unknown |
| đi tắt điều hòa đi | unknown |

### Model: gemma3 | Selector: LLMActionSelector
| User Command | Generated Result |
|--------------|------------------|
| đi tắt điều hòa | turn_on_air_conditioner |
| đi tắt điều hòa đi | turn_on_air_conditioner |

### Model: gemma3 | Selector: LLMActionSelector2
| User Command | Generated Result |
|--------------|------------------|
| bật sáng | unknown |
| bật quạt cho tôi | unknown |
| ti vi bật | unknown |
| ti vi tắt | unknown |
| bật máy lạnh | unknown |
| tắt máy lạnh | unknown |
| đi tắt điều hòa | turn_on_air_conditioner |
| cho tôi tắt điều hòa | unknown |
| làm ơn tắt điều hòa | unknown |
| đi tắt điều hòa đi | turn_on_air_conditioner |
| dừng nhạc | unknown |

### Model: llama3.2 | Selector: LLMActionSelector2
| User Command | Generated Result |
|--------------|------------------|
| bật đèn | unknown |
| bật sáng | unknown |
| làm ơn bật đèn | unknown |
| bật đèn lên | unknown |
| cho tôi bật đèn | unknown |
| tắt đèn | unknown |
| đi tắt đèn | unknown |
| hãy tắt đèn | unknown |
| làm ơn tắt đèn | unknown |
| cho tôi tắt đèn | unknown |
| bật quạt | unknown |
| bật quạt đi | unknown |
| mở quạt | unknown |
| bật quạt cho tôi | unknown |
| làm ơn bật quạt | unknown |
| tắt quạt | unknown |
| quạt tắt | unknown |
| hãy tắt quạt | unknown |
| làm ơn tắt quạt | turn_off_air_conditioner |
| cho tôi tắt quạt | unknown |
| bật ti vi | unknown |
| mở ti vi | unknown |
| ti vi bật | unknown |
| cho tôi bật ti vi | unknown |
| làm ơn bật ti vi | unknown |
| tắt ti vi | unknown |
| ti vi tắt | unknown |
| cho tôi tắt ti vi | unknown |
| mở điều hòa | unknown |
| cho tôi bật điều hòa | unknown |
| làm ơn bật điều hòa | unknown |
| đi bật điều hòa | unknown |
| tắt máy lạnh | unknown |
| làm ơn tắt điều hòa | unknown |
| đi tắt điều hòa đi | unknown |
| phát nhạc | unknown |
| bắt đầu phát nhạc | unknown |
| cho tôi phát nhạc | unknown |
| làm ơn phát nhạc | unknown |
| bắt đầu nhạc | unknown |
| cho tôi dừng nhạc | unknown |
| làm ơn dừng nhạc | unknown |

### Model: phi4-mini | Selector: LLMActionSelector
| User Command | Generated Result |
|--------------|------------------|
| bật sáng | unknown |
| ti vi bật | unknown |

### Model: phi4-mini | Selector: LLMActionSelector2
| User Command | Generated Result |
|--------------|------------------|
| quạt tắt | unknown |
| mở ti vi | unknown |
| làm ơn bật ti vi | unknown |
| ti vi tắt | unknown |
| mở điều hòa | unknown |
| cho tôi bật điều hòa | unknown |
| làm ơn bật điều hòa | unknown |
| đi bật điều hòa | unknown |
| đi tắt điều hòa | unknown |
| cho tôi tắt điều hòa | unknown |
| làm ơn tắt điều hòa | unknown |
| đi tắt điều hòa đi | unknown |

### Model: smollm2 | Selector: LLMActionSelector
| User Command | Generated Result |
|--------------|------------------|
| bật máy lạnh | turn_on_fan |
| tắt máy lạnh | turn_off_fan |
| dừng nhạc | play_music |
| tạm dừng nhạc | play_music |
| làm ơn dừng nhạc | play_music |
| nhạc dừng lại | play_music |

### Model: smollm2 | Selector: LLMActionSelector2
| User Command | Generated Result |
|--------------|------------------|
| bật đèn | unknown |
| bật sáng | unknown |
| làm ơn bật đèn | unknown |
| bật đèn lên | unknown |
| cho tôi bật đèn | unknown |
| tắt đèn | unknown |
| đi tắt đèn | unknown |
| hãy tắt đèn | unknown |
| làm ơn tắt đèn | unknown |
| cho tôi tắt đèn | unknown |
| bật quạt | unknown |
| bật quạt đi | unknown |
| mở quạt | unknown |
| bật quạt cho tôi | unknown |
| làm ơn bật quạt | unknown |
| tắt quạt | unknown |
| quạt tắt | unknown |
| hãy tắt quạt | unknown |
| làm ơn tắt quạt | unknown |
| cho tôi tắt quạt | unknown |
| bật ti vi | unknown |
| mở ti vi | unknown |
| ti vi bật | unknown |
| cho tôi bật ti vi | unknown |
| làm ơn bật ti vi | unknown |
| tắt ti vi | unknown |
| ti vi tắt | unknown |
| hãy tắt ti vi | unknown |
| cho tôi tắt ti vi | unknown |
| làm ơn tắt ti vi | unknown |
| bật máy lạnh | unknown |
| mở điều hòa | unknown |
| cho tôi bật điều hòa | unknown |
| làm ơn bật điều hòa | unknown |
| đi bật điều hòa | unknown |
| tắt máy lạnh | unknown |
| đi tắt điều hòa | unknown |
| cho tôi tắt điều hòa | unknown |
| làm ơn tắt điều hòa | unknown |
| đi tắt điều hòa đi | unknown |
| phát nhạc | unknown |
| bắt đầu phát nhạc | unknown |
| cho tôi phát nhạc | unknown |
| làm ơn phát nhạc | unknown |
| bắt đầu nhạc | unknown |
| dừng nhạc | unknown |
| tạm dừng nhạc | unknown |
| cho tôi dừng nhạc | unknown |
| làm ơn dừng nhạc | unknown |
| nhạc dừng lại | unknown |

