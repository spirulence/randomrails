
#     let [[xLow, yLow], [xHigh, yHigh]] = [coordinate1, coordinate2]
#
#     if (yLow > yHigh || (yLow === yHigh && xLow > xHigh)) {
#       [[xLow, yLow], [xHigh, yHigh]] = [coordinate2, coordinate1]
#     }
#
#     const [dx, dy] = [xHigh - xLow, yHigh - yLow]
#
#     if (dx === 0 && dy === 0 || Math.abs(dx) > 1 || dy > 1) {
#       return false
#     }
#
#     if (yLow % 2 === 0) {
#       return (dx === 0 && dy === 1) || (dx === 1 && dy === 0) || (dx === -1 && dy === 1)
#     } else {
#       return (dx === 0 && dy === 1) || (dx === 1 && dy === 0) || (dx === 1 && dy === 1)
#     }


def are_adjacent(coordinate1, coordinate2):
    [[xLow, yLow], [xHigh, yHigh]] = sorted([coordinate1, coordinate2], key=lambda c: (c[1], c[0]))

    if yLow == yHigh and abs(xLow - xHigh) == 1:
        return True

    dx, dy = xHigh - xLow, yHigh - yLow

    if abs(dx) >= 2 or abs(dy) >= 2:
        return False

    if yLow % 2 == 0:
        return (dx, dy) in {(-1, 1), (0, 1)}
    else:
        return (dx, dy) in {(1, 1), (0, 1)}

