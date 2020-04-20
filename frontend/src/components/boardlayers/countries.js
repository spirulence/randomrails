import React from "react"
import { gridToBoardPixelBoth, gridToBoardPixelX, gridToBoardPixelY, spaceBetween } from "./common"
import { ofType, types } from "../../gamestate"

const CountriesLayer = (props) => {
  const citiesElements = []

  ofType(props.actions, types.ADD_COUNTRY).forEach(action => {
    const [x, y] = action.data.labelPoint
    const name = action.data.name
    citiesElements.push(<text style={{ font: "80px serif", userSelect: "none", fill: "#ddd" }}
                              x={x}
                              y={y} textAnchor={"middle"} >{name}</text>,
    )
  })

  return (
    <g>
      {citiesElements}
    </g>
  )
}

export default CountriesLayer