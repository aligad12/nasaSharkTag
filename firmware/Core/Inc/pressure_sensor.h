/*
 * pressure_sensor.h
 *
 *  Created on: Oct 3, 2025
 *      Author: archlinux
 */

#pragma once

#include <stdint.h>
#include "stm32f4xx_hal.h"

typedef struct
{
    GPIO_TypeDef* dout_port;   /**< DOUT pin port */
    uint16_t      dout_pin;    /**< DOUT pin number */
    GPIO_TypeDef* sck_port;    /**< SCK pin port */
    uint16_t      sck_pin;     /**< SCK pin number */
    int32_t       offset;      /**< Zero offset (raw value at 0 kPa) */
    float         scale;       /**< Scale factor (counts per kPa) */
} HX710B_Cfg;

/**
 * @brief  Initialize HX710B structure and GPIO pins.
 * @param  cfg: Pointer to HX710B configuration structure.
 */
void HX710B_Init(HX710B_Cfg* cfg);

/**
 * @brief  Read raw 24-bit value from HX710B sensor.
 * @param  cfg: Pointer to HX710B configuration structure.
 * @return Raw signed 24-bit value.
 */
int32_t HX710B_ReadRaw(HX710B_Cfg* cfg);

/**
 * @brief  Calibrate zero offset (sensor open to air).
 * @param  cfg: Pointer to HX710B configuration structure.
 */
void HX710B_CalibrateZero(HX710B_Cfg* cfg);

/**
 * @brief  Set scale factor for converting raw counts to kPa.
 * @param  cfg: Pointer to HX710B configuration structure.
 * @param  scale_val: Scale factor (counts per kPa).
 */
void HX710B_SetScale(HX710B_Cfg* cfg, float scale_val);

/**
 * @brief  Read pressure in kilopascals.
 * @param  cfg: Pointer to HX710B configuration structure.
 * @return Pressure in kPa.
 */
float HX710B_ReadPressure(HX710B_Cfg* cfg);

/**
 * @brief  Read depth in meters of water.
 * @param  cfg: Pointer to HX710B configuration structure.
 * @return Depth in meters.
 */
float HX710B_ReadDepth(HX710B_Cfg* cfg);
