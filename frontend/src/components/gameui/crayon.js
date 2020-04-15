import React, { useState } from "react"
import { colorForPlayer } from "../../gamestate"

const CrayonChooser = (props) => {
  const playerId = props.playerId
  const actions = props.actions

  const [isSelectingColor, setIsSelectingColor] = useState(false);

  const options = [
    "#00ffcc", "#0B8A00", "#ffbf00", "#00bfff", "#0000ff", "#bf00ff", "#9900cc", "#cc0099", "#660066",
  ]

  const optionSquares = []
  options.forEach((color) => {
    optionSquares.unshift(<div key={color} style={{ display: "inline-block", width: "30px", height: "30px", backgroundColor: color }} onClick={() => {props.setCrayon(color); setIsSelectingColor(false)}}/>)
  })

  if (!isSelectingColor) {
    return (
      <div style={{ display: "inline-block" }}>
        <button onClick={() => {
          setIsSelectingColor(true)
        }} style={{ backgroundColor: colorForPlayer(actions, playerId) }}>Switch Color
        </button>
      </div>
    )
  } else {
    return (
      <div style={{ display: "inline-block" }}>
        {optionSquares}
      </div>
    )
  }
}

export default CrayonChooser