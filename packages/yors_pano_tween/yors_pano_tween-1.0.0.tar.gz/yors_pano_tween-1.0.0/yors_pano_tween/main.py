import math

class Tween:
    @staticmethod
    def Linear(current_time: float, start_value: float, change: float, duration: float) -> float:
        """
        Linear easing function
        :param current_time: Current time (0 to duration)
        :param start_value: Starting value
        :param change: Change in value (end_value - start_value)
        :param duration: Total duration of animation
        :return: Calculated value at current_time
        """
        return (change * current_time) / duration + start_value

    class Quad:
        @staticmethod
        def easeIn(current_time: float, start_value: float, change: float, duration: float) -> float:
            """
            Quadratic ease-in function
            :param current_time: Current time (0 to duration)
            :param start_value: Starting value
            :param change: Change in value (end_value - start_value)
            :param duration: Total duration of animation
            :return: Calculated value at current_time
            """
            current_time /= duration
            return change * current_time * current_time + start_value

        @staticmethod
        def easeOut(current_time: float, start_value: float, change: float, duration: float) -> float:
            """
            Quadratic ease-out function
            :param current_time: Current time (0 to duration)
            :param start_value: Starting value
            :param change: Change in value (end_value - start_value)
            :param duration: Total duration of animation
            :return: Calculated value at current_time
            """
            current_time /= duration
            return -change * current_time * (current_time - 2) + start_value

        @staticmethod
        def easeInOut(current_time: float, start_value: float, change: float, duration: float) -> float:
            """
            Quadratic ease-in-out function
            :param current_time: Current time (0 to duration)
            :param start_value: Starting value
            :param change: Change in value (end_value - start_value)
            :param duration: Total duration of animation
            :return: Calculated value at current_time
            """
            current_time /= duration / 2
            if current_time < 1:
                return (change / 2) * current_time * current_time + start_value
            current_time -= 1
            return (-change / 2) * (current_time * (current_time - 2) - 1) + start_value

    class Cubic:
        @staticmethod
        def easeIn(t: float, b: float, c: float, d: float) -> float:
            """
            三次方缓动函数（入）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t /= d
            return c * t * t * t + b

        @staticmethod
        def easeOut(t: float, b: float, c: float, d: float) -> float:
            """
            三次方缓动函数（出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t = t / d - 1
            return c * (t * t * t + 1) + b

        @staticmethod
        def easeInOut(t: float, b: float, c: float, d: float) -> float:
            """
            三次方缓动函数（入出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t /= d / 2
            if t < 1:
                return (c / 2) * t * t * t + b
            t -= 2
            return (c / 2) * (t * t * t + 2) + b

    class Quart:
        @staticmethod
        def easeIn(t: float, b: float, c: float, d: float) -> float:
            """
            四次方缓动函数（入）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t /= d
            return c * t * t * t * t + b

        @staticmethod
        def easeOut(t: float, b: float, c: float, d: float) -> float:
            """
            四次方缓动函数（出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t = t / d - 1
            return -c * (t * t * t * t - 1) + b

        @staticmethod
        def easeInOut(t: float, b: float, c: float, d: float) -> float:
            """
            四次方缓动函数（入出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t /= d / 2
            if t < 1:
                return (c / 2) * t * t * t * t + b
            t -= 2
            return (-c / 2) * (t * t * t * t - 2) + b

    class Quint:
        @staticmethod
        def easeIn(t: float, b: float, c: float, d: float) -> float:
            """
            五次方缓动函数（入）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t /= d
            return c * t * t * t * t * t + b

        @staticmethod
        def easeOut(t: float, b: float, c: float, d: float) -> float:
            """
            五次方缓动函数（出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t = t / d - 1
            return c * (t * t * t * t * t + 1) + b

        @staticmethod
        def easeInOut(t: float, b: float, c: float, d: float) -> float:
            """
            五次方缓动函数（入出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            t /= d / 2
            if t < 1:
                return (c / 2) * t * t * t * t * t + b
            t -= 2
            return (c / 2) * (t * t * t * t * t + 2) + b

    class Sine:
        @staticmethod
        def easeIn(t: float, b: float, c: float, d: float) -> float:
            """
            正弦缓动函数（入）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            return -c * math.cos((t / d) * (math.pi / 2)) + c + b

        @staticmethod
        def easeOut(t: float, b: float, c: float, d: float) -> float:
            """
            正弦缓动函数（出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            return c * math.sin((t / d) * (math.pi / 2)) + b

        @staticmethod
        def easeInOut(t: float, b: float, c: float, d: float) -> float:
            """
            正弦缓动函数（入出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            return (-c / 2) * (math.cos((math.pi * t) / d) - 1) + b

    class Expo:
        @staticmethod
        def easeIn(t: float, b: float, c: float, d: float) -> float:
            """
            指数缓动函数（入）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            if t == 0:
                return b
            return c * math.pow(2, 10 * (t / d - 1)) + b

        @staticmethod
        def easeOut(t: float, b: float, c: float, d: float) -> float:
            """
            指数缓动函数（出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            if t == d:
                return b + c
            return c * (-math.pow(2, (-10 * t) / d) + 1) + b

        @staticmethod
        def easeInOut(t: float, b: float, c: float, d: float) -> float:
            """
            指数缓动函数（入出）
            :param t: 当前时间
            :param b: 初始值
            :param c: 变化量
            :param d: 持续时间
            :return: 计算后的数值
            """
            if t == 0:
                return b
            if t == d:
                return b + c
            t /= d / 2
            if t < 1:
                return (c / 2) * math.pow(2, 10 * (t - 1)) + b
            t -= 1
            return (c / 2) * (-math.pow(2, -10 * t) + 2) + b


# Example usage
if __name__ == "__main__":
    current_time = 0.5
    start_value = 0
    change = 100
    duration = 1
    print(Tween.Linear(current_time, start_value, change, duration))
    print(Tween.Quad.easeIn(current_time, start_value, change, duration))
    print(Tween.Cubic.easeOut(current_time, start_value, change, duration))