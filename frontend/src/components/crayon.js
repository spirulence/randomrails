import React, { useState } from "react"

const CrayonChooser = (props) => {
  const [isSelectingColor, setIsSelectingColor] = useState(false);

  const options = [
    "#ff4000", "#0B8A00", "#ffbf00", "#00bfff", "#0000ff", "#bf00ff", "#9900cc", "#cc0099", "#660066", "#00ffcc"
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
        }} style={{ backgroundColor: props.crayon }}>Switch Color
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