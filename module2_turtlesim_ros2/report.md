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

## 문제 3. rclpy 노드 작성

## 문제 4. rclpy 노드 작성