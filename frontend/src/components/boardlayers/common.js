export const spaceBetween = 40
export const dotRadius = 3

export function gridToBoardPixelX(x, y) {
  if (y % 2 === 0) {
    return x * spaceBetween + spaceBetween / 2
  } else {
    return x * spaceBetween + spaceBetween
  }
}

export function gridToBoardPixelBoth(x, y) {
  return `${gridToBoardPixelX(x, y)} ${gridToBoardPixelY(x, y)}`
}

export function gridToBoardPixelY(x, y) {
  return y * spaceBetween + spaceBetween / 2
}

export function areAdjacent(coordinate1, coordinate2) {
  let [[xLow, yLow], [xHigh, yHigh]] = [coordinate1, coordinate2]

  if (yLow > yHigh || (yLow === yHigh && xLow > xHigh)) {
    [[xLow, yLow], [xHigh, yHigh]] = [coordinate2, coordinate1]
  }

  const [dx, dy] = [xHigh - xLow, yHigh - yLow]

  if (dx === 0 && dy === 0 || Math.abs(dx) > 1 || dy > 1) {
    return false
  }

  if (yLow % 2 === 0) {
    return (dx === 0 && dy === 1) || (dx === 1 && dy === 0) || (dx === -1 && dy === 1)
  } else {
    return (dx === 0 && dy === 1) || (dx === 1 && dy === 0) || (dx === 1 && dy === 1)
  }
}