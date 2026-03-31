/*
 * pressure_sensor.c
 *
 *  Created on: Oct 3, 2025
 *      Author: archlinux
 */

#include "pressure_sensor.h"
#include "stm32f4xx_hal.h"

/**
 * @brief  Simple microsecond delay using a busy loop.
 * @param  us: microseconds to delay
 */
static void HX710B_DelayUs(uint32_t us)
{
    uint32_t count = us * (SystemCoreClock / 1000000 / 5);
    while(count--) __NOP();
}

/**
 * @brief  Initialize HX710B pins and structure.
 * @param  cfg: pointer to HX710B configuration
 */
void HX710B_Init(HX710B_Cfg* cfg)
{
    cfg->offset = 0;
    cfg->scale = 1.0f;

    // SCK output
    HAL_GPIO_WritePin(cfg->sck_port, cfg->sck_pin, GPIO_PIN_RESET);
    // DOUT assumed input, pull-up external or module onboard
}

/**
 * @brief  Read 24-bit raw value from HX710B.
 * @param  cfg: pointer to HX710B configuration
 * @return 24-bit signed raw value
 */
int32_t HX710B_ReadRaw(HX710B_Cfg* cfg)
{
    int32_t count = 0;

    // Wait for data ready (DOUT LOW)
    while(HAL_GPIO_ReadPin(cfg->dout_port, cfg->dout_pin) == GPIO_PIN_SET);

    for(int i = 0; i < 24; i++)
    {
        HAL_GPIO_WritePin(cfg->sck_port, cfg->sck_pin, GPIO_PIN_SET);
        HX710B_DelayUs(1);

        count <<= 1;
        HAL_GPIO_WritePin(cfg->sck_port, cfg->sck_pin, GPIO_PIN_RESET);

        if(HAL_GPIO_ReadPin(cfg->dout_port, cfg->dout_pin) == GPIO_PIN_SET)
            count++;
    }

    // 25th pulse for gain (default 128)
    HAL_GPIO_WritePin(cfg->sck_port, cfg->sck_pin, GPIO_PIN_SET);
    HX710B_DelayUs(1);
    HAL_GPIO_WritePin(cfg->sck_port, cfg->sck_pin, GPIO_PIN_RESET);

    // Sign extend 24-bit to 32-bit
    if(count & 0x800000) count |= ~0xFFFFFF;

    return count;
}

/**
 * @brief  Calibrate zero offset (open to air)
 * @param  cfg: pointer to HX710B configuration
 */
void HX710B_CalibrateZero(HX710B_Cfg* cfg)
{
    cfg->offset = HX710B_ReadRaw(cfg);
}

/**
 * @brief  Set scale factor (counts per kPa)
 * @param  cfg: pointer to HX710B configuration
 * @param  scale_val: counts per kPa
 */
void HX710B_SetScale(HX710B_Cfg* cfg, float scale_val)
{
    cfg->scale = scale_val;
}

/**
 * @brief  Read pressure in kPa
 * @param  cfg: pointer to HX710B configuration
 * @return Pressure in kPa
 */
float HX710B_ReadPressure(HX710B_Cfg* cfg)
{
    int32_t raw = HX710B_ReadRaw(cfg);
    return (raw - cfg->offset) / cfg->scale;
}

/**
 * @brief  Read depth in meters of water
 * @param  cfg: pointer to HX710B configuration
 * @return Depth in meters
 */
float HX710B_ReadDepth(HX710B_Cfg* cfg)
{
    float pressure = HX710B_ReadPressure(cfg); // kPa
    return pressure / 9.81f; // convert kPa -> meters of water
}
