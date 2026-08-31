# 모듈 2 과제 - turtlesim 기반 C++Python ROS2 패키지 개발

## 문제 1. c++빌드 체계 세우기

### 1-1. 제동거리 프로그램 빌드 및 실행

'stop_distance.cpp'를 작성하고 C++17과 경고 옵션을 적용하여 빌드하였습니다.

```bash
cd ~/lv1_assignments/module2_turtlesim_ros2/cpp_basics
g++ -Wall -std=c++17 stop_distance.cpp -o stop_distance
./stop_distance
```

실행할 때 속도 '5 m/s', 마찰계수 '0.7'을 입력하였습니다.

```text
속도(m/s)를 입력하세요: 5
마찰계수를 입력하세요: 0.7
제동거리: 1.82 m
```

제동거리는 다음 공식을 사용해 계산하였습니다.

```text
제동거리 = 속도2 / (2 x 마찰계수 x 중력가속도)

제동거리 = 5*5/(2 x 0.7 x 9.81) = 1.82

### 1-2. Motor 클래스의 수동 2단계 빌드

'Motor' 클래스를 다음 세 파일로 분리하였다.

-'motor.hpp': 클래스와 함수 선언
-'motor.cpp': 생성자와 멤버 함수 구현
-'main.cpp': Motor 객체를 생성하고 사용하는 코드

먼저 각 소스 파일을 목적 파일로 컴파일 하였습니다.

```bash
g++ -Wall -std=c++17 -c motor.cpp -o motor.o
g++ -Wall -std=c++17 -c main.cpp -o main.o
```

생성된 목적 파일을 하나의 실행 파일로 링크하였다.

```bash
g++ main.motor.o -o motor_app
````

실행 결과는 다음과 같습니다.

```bash
./motor_app
```

```text
초기 모터속도: 1.5 m/s
변경된 모터 속도: 2 m/s
```

수동된 빌드는 다음 두 단계로 진행됐습니다.

1. 컴파일: '.cpp' 파일을 목적 파일 '.o' 로 변환한다.
2. 링크: 여러 목적 파일을 연결하여 최종 실행 파일을 생성한다.

---

### 1-3. undefined reference 링크 오류 재현

링크 단계에서 Motor 함수의 구현이 담긴 'motor,o'를 일부러 제외하였다.

```bash
g++ main.o -o motor_app_error
```

다음과 같이 'undefined reference' 오류가 발생하였습니다.

```text

undefinde reference to 'Motor::Motor(double)'
undefinde reference to 'Motor::getSeed() const'
undefinde reference to 'Motor::setSpeed(double)'
undefinde reference to 'Motor::getSpeed() const'
collect2: error: ld returnde 1 exit status
```

'main.o' 에는 Motor 함수를 호출한다는 정보만 있고, 실제 함수 구현은 'motor.o'에 들어있다. 링크 명령에서 'motor.o'를 제외했기 때문에 링커가 함수 구현을 찾지 못했습니다.

컴파일 오류와 링크 오류의 차이는 다음과 같습니다.

-컴파일 오류: 문법, 자료형 또는 함수 사용 방식이 잘못되어 소스 파일을 목적 파일로 변환하지 못한경우다.
-링크오류: 각 파일의 컴파일은 성공했지만 필요한 함수 구현이나 목적 파일을 연결하지 못한경우이다.

다음과 같이 'motor.o'를 포함하면 링크가 정상적으로 완료된다.

```bash
g++ main.o motor.o -o motor_app
```

```
### 1-4. CMake 빌드

수동으로 입력했던 컴파일과 링크 과정을 'CMakeLists.txt'에 등록하였습니다.

```cmake
cmake_minomum_required(VERSION 3.22)

project(cpp_basics)

set(CMAKE_CXXS_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_compile_opthions(-Wall)

add_executable(stop_distance stop_distance.cpp)
add_executable(motor_app main.cpp motor.cpp)
```

소스와 빌드 결과를 분히라기 위해 'build' 디렉터리에서 빌드하였다.

```bash
cd ~/lv1_assignments/module2_turtlesim_ros2/cpp_basics
mkdir -p build
cd build
cmake ..
make
```

빌드 결과 두 실행 파일이 생성되었습니다.

```text
Built target stop_distance
Built target motor_app
```

생성된 프로그램을 실행하여 수동 비륻와 같은 결과가 나오는 것을 확인하였다.

```bash
./motor_app
./stop_distance
```

---

### 1-5.  중분 빌드 확인

'motor.cpp'의 'setSpeed()'를 수정하여 음수 속도가 입력되면 '0.0'으로 저장하도록 변경하였다.

```cpp
void Motor::setSpeed(double speed) {
    if (speed < 0.0) {
        speed_ = 0.0;
    }else {
        speed_ = speed;
    }
}
```
수정 후 'make'를 다시 실행하였습니다.

```bash
cd ~/lv1_assignments/module2_turtlesim_ros2/cpp_basics/build
make
```

출력은 다음과 같습니다.

```text
Consolidate compiler generated dependencies of target stop_distance
[ 40%] Built target stop_distance
Consolidate compiler generated dependencies of target motor_app
[ 60%] Building CXX object CMakeFiles/motor_app.dir/motor.cpp.o
[ 80%] Linking CXX executable motor_app
[100%] Built target motor_app
```

다시 컴파일된 파일은 'motor.cpp'뿐이었다. 수정하지 않은 'main.cpp'와 'stop_distance.cpp'는 다시 컴파일 되지 않았다. 다만 'motor.cpp.o'가 변경되었으므로 최종 실행 파일 'motor_app'은 다시 링크 되었습니다.

중분 빌드는 파일의 수정 시각과 소스 파일 사이의 의존 관계를 확인하여, 변경된 파일과 그파일에 영향을 받는 대상만 다시 빌드합니다. 따라서 전체 프로젝트를 매번 빌드하는것보다 빌드 시간을 줄일수 있습니다.

## 문제 2. 현대 C++로 센서 계층 구현

### 2-1. 추상 클래스와 다형성

순수 가상 함수 'naem()'과 'read()'를 가진 추상 클래스 'Sensor'를 만들고, 이를 상속하는 'Lidar'와 'Imu' 클래스를 구현하였습니다.

```cpp
class Sensor {
public:
    virtual ~Sensor() {
        std::cout << "Sensor 소멸" std::endl;
    }

    virtual std::string name() const = 0;
    virtual double read() const = 0;
};
```

서로 다른 센서 객체를 다음과 같이 하나의 컨테이너에 저장하였습니다.

```cpp
std::vector<std::unique_ptr<Sensor>> sensors;

sensors.push_back(
    std::make_unique<Imu>(9.81)
);
```

부모 클래스인 'Sensor' 포인터를 통해 각 자식 클래스의 'name()'과 'read()'가 실행되는 것을 확인하였습니다.

```text
Lidar생성
Imu 생성

센서 측정 결과
Lidar: 3.5
Imu: 9.81
Lidar 소멸
Sensor 소멸
Imu 소멸
Sensor 소멸
```

같은 'Sensor' 포인터를 사용했지만 실제 객체의 종류에 따라 'Lidar::read()' 또는 'Imu::read()'가 실행되었다.

---

### 2-2. 스택 객체와 힙 객체의 소멸 시점

지역 변수로 만든 'Lidar' 객체와 'std::make_unique'로 생성한 'Imu' 객체의 소멸 시점을 확인하였다.

```text
[1] 스택 객체 생성
Lidar 생성
스택 Lidar 측정값: 2.5
Lidar 소멸
Sensor 소멸
스택 객체 블록 종료

[2] unique_ptr 힙 객체 생성
Imu 생성
힙 Imu 측정값: 9.81
Imu 소멸
Sensor 소멸
unique_ptr 블록 종료
```

스택 객체인 'stack_lidar'는 객체가 선언된 중괄호 블록을 벗어날때 자동으로 소멸하였습니다.
힙 객체는 'std::make_unique'로 생성하였으며, 해당 객체를 소유한 'unique_ptr'가 블록을 벗어날 때 자동으로 메모리가 해제되었습니다. 두방식 모두 RAII를 사용하므로 내가 직접 'delete'를 호출하지 않아도 객체가 안전하게 정리된다.

### 2-3. 가상 소멸자를 제거했을 때의 차이

부모 클래스의 소멸자에서 'virtual'을 제거한 뒤 부모 포인터를 통해 자식 객체를 삭제하였다.

빌드 과정에서 다음 경고가 발생하였다.

```text
warning deleting object of abstract class tyep
'NonVirtualSensor' which has non-virtual destructor
will cause undefined behavior
[-Wdelete-non-virtual-dtor]
```

실행 결과는 이렇게 나왔습니다.

```text
NonVirtualLidar 생성
측정값: 4.2
NonvirtuaSensor 소멸
```

'NonvirtualLidar 소멸'이 출력되지 않고 부모 클래스의 소멸자만 실행되었다. 부모 포인터를 통해 자식 객체를 삭제할 때 부모 소멸자가 가상 함수가 아니면 자식 소멸자가 정상적으로 호출된다는 보장이 없으며, 이거는 정의되지 않은 동작을 발생시킵니다. 따라서 다형성에 사용하는 부모 클래스에 다음과 같이 가상 소멸자가 필요하다.

```cpp
virtual ~Sensor() = default;
```

---

### 2-4. STL 컨테이너와 알고리즘 사용

센서 이름과 최근 측정값을 연결하기 위해 'std::unordered_map'을 사용하였습니다.

```cpp
std::unordered_map<std::string, double>
    latest_measurements;

latest_measurements["Lidar"] = 2.5;
latest_measurements["Imu"] = 9.81;
```
측정 로그는 'std::vector'에 저장하고, 'std::count_if'를 사용하여 목표점까지 거리가 '0.5' 이하인 기록을 계산하였습니다.

```text
[3] 최근 Lidar 측정값: 2.5
[4] 목표점까지 거리 0.5 이하 기록: 3개
```

전체 기록 네개중 거리가 '0.25', '0.50', '1.0'인 세개의 기록이 조건을 만족했습니다.

---

### 2-5. 함수 탬플릿 clamp

자료형에 관계없이 값을 지정한 범위로 제한할 수 있도록 함수 탬플릿을 작성하였습니다.

```cpp
tamplate <typename T>
T clam(T value, T minmum, T maximum) {
    if (value <minimum) {
        return minimum;

    }

    if (value > maximum) {
    return maximum;
    }

    return value;
}
```

'double' 속도와 'int' 픽셀값에 각각 적용하였습니다.

```cpp
double limited_speed =
    clamp(1.8, 0.0, 1.0);

int limited_pixel =
    clamp(300, 0, 255);
```

실행 결과는 다음과 같다.

```text
[5] 제한된 속도: 1
[6] 제한된 픽셀값: 255
```

입력한 속도 '1.8'은 최대값 '1.0'으로 제한되었고, 픽셀값 '300'은 최대값 '255'로 제한되었다. 하나의 함수 탬플릿을 'double'과 'int'자료형에 모두 적용할 수 있었다.

---
### 2-6. 메모리 누수 재현

반복문에서 'new'로 'Lidar' 객체 10개를 생성하고 'delete'를 호출하지 않아 메모리 누수를 발생시켰습니다.

```bash
valgrind --leak-check=full ./sensor_bulid/deak_demo
```

Valgrind 검사 결과는 다음과 같다.

```text
HEAP SUMMRY:
    in use at exit: 160 bytes in 10 blocks
    total heap usage: 12 allocs, 2 frees, 73,888 bytes allocated

LEAK SUMMARY:
    definitely lost: 160 bytes in 10 blocks
    indirectly lost: 0 bytes in 0 blocks
    possibly lost: 0 bytes in 0 blocks
    still reachable: 0 bytes in 0 blocks

ERROR SUMMARY: 1 errors from 1 contexts
```

'Lidar' 객체 10개에 해당하는 총 '160 bytes'가 해제되지 않은 것으로 확인되었습니다.

---

### 2-7. unique_ptr를 사용한 누수 해결

'new'로 직접 생성하던 코드를 'std::make_unique'로 수정하였다.

```cpp
for (int index = 1; index <= 10; ++index) {
    auto sensor=
        std::make_unique<Lidar>(index);

    std::cout << index << "번째 측정값:"
              << sensor->read()
              << std::endl;
}
```

각 반복이 끝날 때 'unique_ptr'가 소멸하면서 'Lidar'와 'Sensor'의 소멸자가 자동으로 실행되었습니다.

```text
Lidar 생성
1번째 측정값:1
Lidar 소멸
Sensor 소멸
...
Lidar 생성
10번째 측정값:10
Lidar 소멸
Sensor 소멸
```

수정 후 Valgrind 결과는 다음과 같다.

```text
HEAP SUMMRY:
        in use at exit: 0 bytes in 0 blocks
        total heap usege: 12 allocs, 12 free, 73,888 bytes allocated

ALL heap blocks were freed -- no leaks are possible

ERROR SUMMARY: 0 errors from 0 contexts
```

수정 전에는 '160 bytes in 10 blocks'가 누수되었지만, 'std::make_uniqe'로 변경한 뒤 모든 메모리가 자동으로 해제 되었습니다. 스마트 포인터를 사용하면 객체의 소유권과 수명이 명확해지고, 'delete' 누락으로 인한 메모리 누수를 방지할수 있습니다.

## 문제 3. rclpy 노드 작성

## 문제 4. rclpy 노드 작성
