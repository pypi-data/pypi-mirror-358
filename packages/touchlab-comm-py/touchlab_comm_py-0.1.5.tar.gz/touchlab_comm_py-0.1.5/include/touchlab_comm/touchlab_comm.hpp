// Copyright (c) 2022 Touchlab Limited. All Rights Reserved
// Unauthorized copying or modifications of this file, via any medium is strictly prohibited.

#ifndef TOUCHLAB_COMM__TOUCHLAB_COMM_HPP_
#define TOUCHLAB_COMM__TOUCHLAB_COMM_HPP_

#include <map>
#include <memory>
#include <string>
#include <vector>

/**
 * \mainpage Touchlab Communication Library
 * \section core Main classes
 * * \link touchlab_comm::TouchlabComms main class \endlink.
 *
 */

namespace touchlab_comm
{
/**
 * @class TouchlabComms touchlab_comm.h touchlab_comm/touchlab_comm.h
 * @brief Touchlab communication main class.
 *
 */
class TouchlabComms
{
public:
  /**
   * @brief Construct a new Touchlab Comms object
   *
   */
  TouchlabComms();

  /**
   * @brief Destroy the Touchlab Comms object
   *
   */
  virtual ~TouchlabComms();

  /**
   * @brief Init comm
   *
   * @param filename path to the sensor param binary file
   */
  void init(const std::string & filename = "");

  /**
   * @brief Connect to the sensor
   *
   * @param port Serial port name, e.g. `COM1`, or `/dev/ttyACM0`.
   *
   */
  void connect(const std::string & port);

  /**
   * @brief Read raw signal
   *
   * @param data Returned raw data vector from the latest data packet
   * @param timeout Timeout in ms
   */
  void read_raw(std::vector<double> & data, int64_t timeout = 500.0);

  /**
   * @brief Read calibrated data
   *
   * @param data Return data calibrated by the model defined by the SensorParameters class
   * @param timeout Timeout in ms
   */
  void read(std::vector<double> & data, int64_t timeout = 500.0);

  /**
   * @brief Get the version of the API
   *
   * @return std::string Version string
   */
  static std::string get_version();

  /**
   * @brief Returns if the sensor is connected and communicating
   *
   * @return std::string True if connected
   */
  bool is_connected();

  /**
   * @brief Zero out sensor offset
   *
   * @param ind Optional vector of sensor indices to zero out. If empty, all taxels will be zeroed.
   */
  void zero(const std::vector<int>& ind = {});

  /**
   * @brief Zero out sensor offset with custom data
   *
   * @param data Custom data used to zero the sensor. Inner vector should have one element for each taxel. The outer vector should contain n samples of input data.
   * @param ind Optional vector of sensor indices to zero out. If empty, all taxels will be zeroed.
   */
  void zero(const std::vector<std::vector<double>>& data, const std::vector<int>& ind = {});

  /**
   * @brief Translate raw data sample into calibrated values
   *
   * @param raw Input raw data
   * @param calibrated Output calibrated data
   */
  void translate(const std::vector<double>& raw, std::vector<double>& calibrated);

private:
  class Implementation;
  std::unique_ptr<Implementation> impl_;
};

}  // namespace touchlab_comm

#endif  // TOUCHLAB_COMM__TOUCHLAB_COMM_HPP_
