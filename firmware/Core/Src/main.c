/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "i2c.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
SIM800_t SIM800;
HX710B_Cfg HX710B = {.dout_pin = PRESSURE_OUT_Pin, .dout_port = PRESSURE_OUT_GPIO_Port,
					.sck_pin = PRESSURE_CLK_Pin, .sck_port = PRESSURE_CLK_GPIO_Port};
float temp_value = 0;
float depth;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
int _close(int file) { return -1; }
int _fstat(int file, void *st) { return 0; }
int _isatty(int file) { return 1; }
int _lseek(int file, int ptr, int dir) { return 0; }
int _read(int file, char *ptr, int len) { return 0; }
int _kill(int pid, int sig) { return -1; }
int _getpid(void) { return 1; }

int _write(int file, uint8_t* p, int len)
{
	if(HAL_UART_Transmit(&huart2, p, len, len) == HAL_OK )
	{
		return len;
	}
	return 0;
}
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart == UART_SIM800) {
        Sim800_RxCallBack();
    }
	if(huart == &huart1) {
		GPS_UART_CallBack();
	}
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  SIM800.sim.apn = APN;								// For WE Egypt apn is "internet"
  SIM800.sim.apn_user = APN_KEY;
  SIM800.sim.apn_pass = APN_PASS;
  SIM800.mqttServer.host = MQTT_HOST;
  SIM800.mqttServer.port = MQTT_PORT;
  SIM800.mqttClient.username = MQTT_USERNAME;
  SIM800.mqttClient.pass = MQTT_PASS;
  SIM800.mqttClient.clientID = MQTT_CLIENT_ID;
  SIM800.mqttClient.keepAliveInterval = MQTT_KEEP_ALIVE;
  MQTT_Init();
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  MX_TIM10_Init();
  MX_I2C1_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */
  HX710B_Init(&HX710B);
  HX710B_CalibrateZero(&HX710B);
  HX710B_SetScale(&HX710B, 26000.0f);
  HAL_TIM_Base_Start(&htim10);
  DS18B20_Init(GPIOB, GPIO_PIN_9, &htim10);
  MPU6050_Initialization();
  GPS_Init();
  HAL_Delay(1000);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  char buf[128];
  int len = 0;
  while (1)
  {
	    // int32_t raw = HX710B_ReadRaw(&HX710B);
	    // float pressure = HX710B_ReadPressure(&HX710B);
	    // Read depth
	    depth = HX710B_ReadDepth(&HX710B);
	    depth = (depth <= 0) ? 0 : depth;
	    len = snprintf(buf, sizeof(buf), "%.2f", depth);  // depth first, no trailing comma yet

	    // Read temperature
	    temp_value = DS18B20_ReadTemp();
	    temp_value = (temp_value <= -100) ? 0 : temp_value;
	    len += snprintf(buf + len, sizeof(buf) - len, ",%.2f", temp_value);  // append temp

	    // Read MPU6050 if ready
	    //if (MPU6050_DataReady() == 1)
	    //{
	        MPU6050_ProcessData(&MPU6050);
	        len += snprintf(buf + len, sizeof(buf) - len, ",%.2f,%.2f,%.2f",
	                        MPU6050.acc_x, MPU6050.acc_y, MPU6050.acc_z);
	    //}
	        //if (GPS.lock) // GPS has fix
		    //{
	        	len += snprintf(buf + len, sizeof(buf) - len, ",%.6f,%.6f",
	        			GPS.dec_latitude, GPS.dec_longitude);
		    //}


		if(0 == SIM800.mqttServer.connect)
		{
	    	MQTT_Init();
			HAL_Delay(1000);
		}
		if(1 == SIM800.mqttServer.connect)
		{
			MQTT_Pub("abdelrhmanatta/feeds/shark", buf);
			HAL_Delay(5000);
		}
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 12;
  RCC_OscInitStruct.PLL.PLLN = 96;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
