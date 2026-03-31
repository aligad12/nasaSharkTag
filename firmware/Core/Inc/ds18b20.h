/*
 * ds18b20.h
 *
 *  Created on: Oct 1, 2025
 *      Author: archlinux
 */

#pragma once

#include <stdint.h>
#include "stm32f4xx_hal.h"

typedef struct
{
	GPIO_TypeDef* port;
	uint16_t pin;
	TIM_HandleTypeDef* timer;
}DS18B20_Cfg;

/*
 *
 */
void DS18B20_Init(GPIO_TypeDef* port, uint16_t pin, TIM_HandleTypeDef* timer);

/*
 *
 */
uint8_t DS18B20_Start(void);

/*
 *
 */
void DS18B20_Write(uint8_t data);

/*
 *
 */
uint8_t DS18B20_Read(void);

/*
 *
 */
float DS18B20_ReadTemp(void);

