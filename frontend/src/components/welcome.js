import React, { useEffect, useState } from "react"
import ColorSelectorSquares from "./lobby/colorselectorsquares"

const Welcome = (props) => {
  const animationLength = 15
  const frameTime = 120
  const [animationState, setAnimationState] = useState(0)
  const [isAnimating, setIsAnimating] = useState(true)

  useEffect(() => {
    if (isAnimating) {
      const interval = setInterval(() => {
        setAnimationState((animationState + 1) % animationLength)
      }, frameTime)
      return function() {
        clearInterval(interval)
      }
    }
  }, [animationState, isAnimating])

  const spinnerElements = []
  for (let i = 0; i < animationState; i++) {
    spinnerElements.unshift(<h1 style={{ display: "inline" }}>=</h1>)
  }

  return (
    <div style={{ position: "fixed", top: "35%", width: "100%" }}>
      <div style={{ maxWidth: "600px", padding: "5px", margin: "auto" }}>
        <h1>Random Rails</h1>
        {spinnerElements}
      </div>
    </div>
  )
}

export default Welcome