"""
agnflow 用法示例
"""

from typing import TypedDict
from agnflow import Node, Flow


# ✨一、状态定义（使用TypedDict）
class State(TypedDict):
    data: str


state: State = {"data": "test"}


# ✨二、定义工作流节点

# 节点函数入参：根据变量名，自动从state中获取参数并且注入，默认为注入整个state
# 节点函数返回值：返回 (action, state) ，action用于导航到下一个节点，state 用于更新状态


# 方法1：使用类继承Node
class A(Node):
    def exec(self, data):
        print(f"A exec {data}")
        import random

        a = random.choices(["c", "b"], weights=[0.7, 0.3])
        return a

    async def aexec(self, data):
        print(f"A exec {data}")
        import random

        a = random.choices(["c", "b"], weights=[0.7, 0.3])
        return a


class B(Node):
    def exec(self, state):
        print(f"B exec {state}")

    async def aexec(self, state):
        print(f"B exec {state}")


class C(Node):
    def exec(self, state):
        print(f"C exec {state}")
        return "a", {"data": "test:C"}

    async def aexec(self, state):
        print(f"C exec {state}")
        return "a", {"data": "test:C"}


# 方法2：使用函数和Node的exec和aexec参数
def d1_exec(data):
    print(f"d1 exec {data}")
    return "a", {"data": "test:d1"}


async def d1_aexec(data):
    print(f"d1 aexec {data}")
    return "a"  # 返回 action，用于导航到下一个节点


def d2_exec(state):
    print(f"d2 exec {state}")
    return "exit"


async def d2_aexec(state):
    print(f"d2 aexec {state}")
    return "exit", {"data": "test:d2"}


a = A()
b = B()
c = C()
b2 = C()
d1 = Node(exec=d1_exec, aexec=d1_aexec)
d2 = Node(exec=d2_exec, aexec=d2_aexec)

flow = Flow()
flow2 = Flow()
flow3 = Flow()

# ✨三、连接工作流节点
# 示例
# a >> "b" >> b >> "c" >> c  # 正向连接
# c << "c" << b << "b" << a  # 反向连接
# a >> [b >> flow3 >> b2, c >> a]  # 循环多分支


flow2[d1 >> [flow[a >> [b >> flow3[b2], c >> a]]]] >> d2

# print(flow2.hidden_connections)
# print(flow2.connections)

# ✨四、执行工作流
# flow2.run(state)
# asyncio.run(flow2.arun(state))

# ✨五、绘制流程图
print(flow2.render_mermaid(saved_file="./assets/example_mermaid.png"))
