import numpy as np

from src.transform import inv_T, make_T
from src.rotation import rot_x, rot_y, rot_z

class CoordinateChain:
    def __init__(self):
        self.transforms = {}

    def add(self, parent, child, T):
        self.transforms[(parent,child)] = np.asarray(T, dtype=float)

    def get(self,parent, child):
        return self.transforms[(parent,child)]

    def T_from_root(self, frame):
        parent_map = {
            child: (parent, T)
            for(parent, child), T in self.transforms.items()
        }
        # if문: 조건이 참일 때 아래 코드를 실행하는 조건문
        # frame이 parent_map에 없다는 뜻은 더이상 부모가 없다는 뜻
        if frame not in parent_map:

            # np,eye(4): 4x4 단위행렬을 만드는 Numpy 함수
            # 회전도 이동도 없는 변환을 의미
            return np. eye(4)

        # 딕셔너리에서 frame을 key로 사용해 값을 꺼냄
        # 튜플 언패킹: ("link", T행렬)을 parent와 T 두 변수에 나눠 저장
        Parent, T = parent_map[frame]

        # 재귀 호출: 같은 함수가 자기 자신을 다시 호출하는 문법
        # 먼저 parent가 root(base)에서 어디에 있는지 구한 뒤,
        # 현재 parent -> frame 변화 T를 고햅서 root -> frame 변환을 완성
        return self.T_from_root(parent) @ T

    def T(self, target,source):
        # [역활] root(base) -> target 변환행렬을 구함
        # [이유] source와 target 사이의 변환을 계산하기 위한 재료
        T_root_target = self.T_from_root(target)

        #[역활] root(base) -> source 변환헹렬을 구함
        #[이유] source가 base 기준으로 어디에 있는지 알아야 하기 때문
        T_root_source = self.T_from_root(source)
        #[문법] 함수 호출 + @ 행렬 곱셈
        #[이유] 두 좌표계가 root(base) 기준으로 어디 있는지 알았으므로,
        #       source에서 root로 돌아간 뒤 target 기준으로 바꾸기 위해
        return inv_T(T_root_target) @ T_root_source
    def transform(self, target, source, points):
        #[문법] np.asarray(): 입력값을 NumPy 배열 형태로 바꾸는 함수
        #[역활] 리스트로 들어오든 배열로 들어오든 계산 가능한 형태로 동일
        #[이유] 이후 행렬 연산으로 안정적으로 하기 위해
        P = np.asarray(points, dtype=float)

        #[문법] 클래스 내부 메서드 호출
        # [역활] source -> target 좌표변환 행렬을 가져옴
        # [이유] 실제 점 좌표를 변환하려면 먼저 변환행렬 T가 필요하기 때문
        T = self.T(target,source)    
        # [문법] if 조건문: 조건이 True일 때만 아래 코드를 실행
        # [문법] ndim: Numpy 배열이 몇 차원인지 알려주는 속성
        # [역활] points가 점 하나 [x, y, z]인지 확인
        # [이유] 점 하나와 점 여러 개는 배열 모양이 달라서 계산 방법을 나눠야 함
        if P.ndim == 1:

            # [문법]np.append(): 배열 뒤에 값을 하나 추가하는 함수
            # [역활] [x, y, z] -> [x, y, z,1.0] 으로 만듦
            # [이유] 우리가 만든 T는 4x4 동차변환행렬이라서
            #   3개짜리 좌표가 아니라 4개짜리 동차좌표가 필요함
            p_h = np.append(P, 1.0) # 1은 '나는 방향 벡터가 아니라 실제 공간에 존재하는 점이니까 이동도 적용해줘ㅠ'

            #[문법] @ : NumPy 행렬 곱셈 연산자
            #[역활] source 좌표의 점을 target 좌표로 실제 변환
            #[이유] T 안에 회전과 이동 정보가 들어 있으므로,
            #       점에 T를 곱해야 새로운 좌표가 계산됨
            result = T @ p_h

            #[문법] [:3] : 배열의 0, 1, 2번째 값만 가져오는 슬라이싱
            #[역활] [x, y, z, 1] 중 실제 좌표인 [x, y, z]만 반환
            #[이유] 마지막 값은 동차좌표 계산용이므로 최종 좌표에는 필요없음
            return result[:3]

        #[문법] np.ones(): 값이 모두 1인 Numpy 배열을 만드는 함수
        #[역활] 점의 개수 N만큼 1을 만들어서 (N,1) 모양의 열을 만듦
        #[이유] 모든 [x, y, z] 점 뒤에 1을 붙여 동차좌표로 만들기 위해
        ones = np.ones((P.shape[0], 1))

        # [문법] np.hstack(): 배열을 가로 방향으로 이어 붙이는 함수
        # [역활] (N,3) 좌표와 (N,1)의 1 열을 합쳐 (N,4)로 만듦
        # [이유] 4x4 동차변환행렬 T와 곱할 수 있게 만들기 위해
        P_h = np.hstack([P, ones])

        #[문법] @ : 행렬곱셈, T.T : 행렬 T를 전치(transpose)
        #[역활] 모든 짐을 source 좌표계에서 target 좌표계로 한 번에 변환
        #[이유] for문으로 점을 하나씩 계산하지 않고 NumPy 행렬 연산으로 빠르게 처리하기 위해
        result_h = P_h @ T.T

        # [문법] [:, :3] : 모든 행에서 앞의 3개 열만 가져오는 슬라이싱
        # [역활] [x, y, z, 1]중 실제 좌표인 [x, y, z]만 남김
        # [이유] 마지막 1은 동차좌표 계산용 값이라 최종 좌표에는 필요 없기 때문
        return result_h[:, :3]

    def default_chain():
        # [문법] 함수 호출: Coordinatechain 클래스의 객체를 하나 생성
        # [역활] base, link, camera 관계를 저장할 새로운 좌표계 체인을 만듦
        # [이유] 앞으로 좌표계들의 부모-자식 관계를 여기에 하나씩 등록해야 하기 때문
        chain = CoordinateChain()

        # [문법] np.deg2rad(): 각도를 도(deg)
        # [역활] 30도를 rot_z()가 사용할 수 있는 라디안 값으로 바꿈
        # [이유] 우리가 만든 rot_z() 내부의 np.sin(), np.cos()는 라디안을 사용하기 때문
        R_base_link = rot_z(np.deg2rad(30.0))

        # [문법] 함수 호출: make_T(회정행렬, 이동벡터)
        # [역활] base -> link의 회전과 이동을 하나의 4x4 변환 행렬로 합침
        # [이유] 로봇 좌표변환에서는 회전만이 아닐라 위치 이동도 같이 처리해야 하기 때문
        T_base_link = make_T(R_base_link, [0.30, 0.00, 0.40]) 

        # [문법] 객체의 메서드 호출: chain.add(부모, 자식, 변환행렬)
        # [역활] base -> link 관계와 T_base_link를 chain에 저장
        # [이유] 나중에 chain이 여러 좌표계를 자동으로 이어서 계산할 수 있게 하기 위해
        chain.add("base", "link", T_base_link)
        # [문법] np.deg2rad(): 각도를 도(degree)에서 라디안(radian)으로 변환
        # [역활] 30도를 rot_z()가 사용할 수 있는 라디안 값으로 바꿈
        # [이유] 우리가 만든 rot_z() 내부의 np.sin(), np.cos()는 라디안을 사용하기 때문
        R_base_link = rot_z(np.deg2rad(30.0))
        # [문법] 함수 호출: make_T(회정행렬, 이동백터)
        # [역활] base -> link의 회전과 이동을 하나의 4x4 변환행렬 합침
        # [이유] 로봇 좌표변환에서는 회전만이 아니라 위치 이동도 같이 처리해야하기 때문에
        chain.add("base", "Link", T_base_link)
        # [문법] 객체의 메서드 호출: chain.add(부모, 자식, 변환행렬)
        # [역활] base -> link관계와 T_base_link를 chain에 저장
        # [이유] 나중에 chain이 여러 좌표계를 자동으로 계산할 수 있게 하기 위해
        

