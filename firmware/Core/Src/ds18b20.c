/*
 * ds18b20.c
 *
 *  Created on: Oct 1, 2025
 *      Author: archlinux
 */

#include "ds18b20.h"

// Static configuration
static GPIO_TypeDef* DS18B20_PORT = NULL;
static uint16_t DS18B20_PIN = 0;
static TIM_HandleTypeDef* DS18B20_TIMER = NULL;

// Private functions
static void delay_us(uint16_t us);
static void setPinOutput(void);
static void setPinInput(void);

void DS18B20_Init(GPIO_TypeDef* port, uint16_t pin, TIM_HandleTypeDef* timer)
{
    DS18B20_PORT = port;
    DS18B20_PIN = pin;
    DS18B20_TIMER = timer;

    // Initialize pin as input with pull-up once
    setPinInput();
}

static void delay_us(uint16_t us)
{
    if (!DS18B20_TIMER) return;

    uint32_t start = __HAL_TIM_GET_COUNTER(DS18B20_TIMER);
    uint32_t target = start + us;

    if (target > 0xFFFF) {
        while (__HAL_TIM_GET_COUNTER(DS18B20_TIMER) >= start);
        start = 0;
        target = us;
    }

    while (__HAL_TIM_GET_COUNTER(DS18B20_TIMER) < target);
}

static void setPinOutput(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = DS18B20_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(DS18B20_PORT, &GPIO_InitStruct);
}

static void setPinInput(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = DS18B20_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(DS18B20_PORT, &GPIO_InitStruct);
}

uint8_t DS18B20_Start(void)
{
    if (!DS18B20_PORT) return 0;

    uint8_t Response = 0;
    __disable_irq();

    setPinOutput();
    HAL_GPIO_WritePin(DS18B20_PORT, DS18B20_PIN, 0);
    delay_us(480);

    setPinInput();
    delay_us(80);

    if (!HAL_GPIO_ReadPin(DS18B20_PORT, DS18B20_PIN)) {
        Response = 1;
    }

    delay_us(400);
    __enable_irq();
    return Response;
}

void DS18B20_Write(uint8_t data)
{
    if (!DS18B20_PORT) return;

    __disable_irq();
    for(int i = 0; i < 8; i++)
    {
        setPinOutput();
        HAL_GPIO_WritePin(DS18B20_PORT, DS18B20_PIN, 0);
        delay_us(1);

        if(data & (1 << i)) {
            setPinInput(); // Release for '1'
        }

        delay_us(60);
        setPinInput(); // Always end with input
    }
    __enable_irq();
}

uint8_t DS18B20_Read(void)
{
    if (!DS18B20_PORT) return 0;

    uint8_t value = 0;
    __disable_irq();

    for(int i = 0; i < 8; i++)
    {
        setPinOutput();
        HAL_GPIO_WritePin(DS18B20_PORT, DS18B20_PIN, 0);
        delay_us(2);

        setPinInput();
        delay_us(10); // Small delay before sampling

        if(HAL_GPIO_ReadPin(DS18B20_PORT, DS18B20_PIN)) {
            value |= (1 << i);
        }

        delay_us(50); // Complete the 60µs slot
    }

    __enable_irq();
    return value;
}

float DS18B20_ReadTemp(void)
{
    if (!DS18B20_PORT) return -999.9f;

    uint8_t temp_l, temp_h;
    int16_t temp_raw;
    uint8_t attempts = 3;

    while (attempts--) {
        if(DS18B20_Start()) {
            DS18B20_Write(0xCC); // Skip ROM
            DS18B20_Write(0x44); // Convert Temp
            HAL_Delay(750);

            if(DS18B20_Start()) {
                DS18B20_Write(0xCC);
                DS18B20_Write(0xBE); // Read scratchpad

                temp_l = DS18B20_Read();
                temp_h = DS18B20_Read();

                temp_raw = (temp_h << 8) | temp_l;

                // Validate reading
                if (temp_raw != 0xFFFF && temp_raw != 0x0000) {
                    return (float)temp_raw / 16.0f;
                }
            }
        }
        HAL_Delay(10);
    }
    return -999.9f;
}
