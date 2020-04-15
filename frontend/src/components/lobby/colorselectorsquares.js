import React, { useState } from "react"

const ColorSelectorSquares = (props) => {
  const optionSquares = []
  props.colorOptions.forEach((option, index) => {
    optionSquares.push(<div key={option.color} style={{
      display: "inline-block",
      width: "60px",
      margin: "10px",
      height: "30px",
      backgroundColor: option.color,
      opacity: option.available ? "1" : "0.2",
      border: option.available ? "none" : "dotted 5px red",
      boxShadow: index === props.selectedColorIndex ? "5px 5px 5px" : "none",
    }} onClick={() => {
      if (option.available) {
        props.selectColor(index)
      }
    }}/>)
  })


  return (
    <div style={{ display: "inline-block" }}>
      {optionSquares}
    </div>
  )
}

export default ColorSelectorSquares