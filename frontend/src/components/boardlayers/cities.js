import React from "react"
import { graphql, useStaticQuery } from "gatsby"
import { default as moji } from "../openmoji"
import { gridToBoardPixelBoth, gridToBoardPixelX, gridToBoardPixelY, spaceBetween } from "./common"
import { ofType, types } from "../../gamestate"

const cityFill = "rgba(255,0,0,0.65)"

const CitiesLayer = (props) => {
  const citiesElements = []

  ofType(props.actions, types.ADD_MAJOR_CITY).forEach(action => {
    const [x, y] = action.data.location
    const name = action.data.name
    if (y % 2 === 0) {
      citiesElements.unshift(
        <g key={name}>
          <path fill={cityFill}
                d={`M ${gridToBoardPixelBoth(x - 1, y - 1)} 
      L ${gridToBoardPixelBoth(x, y - 1)} 
      L ${gridToBoardPixelBoth(x + 1, y)}
      L ${gridToBoardPixelBoth(x, y + 1)}
      L ${gridToBoardPixelBoth(x - 1, y + 1)}
      L ${gridToBoardPixelBoth(x - 1, y)}`}/>
          <text style={{ font: "30px sans-serif", userSelect: "none" }}
                x={gridToBoardPixelX(x - 1, y + 2)}
                y={gridToBoardPixelY(x - 1, y + 2) - 5}>{name}</text>
        </g>,
      )
    } else {
      citiesElements.unshift(
        <g key={name}>
          <path fill={cityFill}
                d={`M ${gridToBoardPixelBoth(x, y - 1)} 
      L ${gridToBoardPixelBoth(x + 1, y - 1)} 
      L ${gridToBoardPixelBoth(x + 1, y)}
      L ${gridToBoardPixelBoth(x + 1, y + 1)}
      L ${gridToBoardPixelBoth(x, y + 1)}
      L ${gridToBoardPixelBoth(x - 1, y)}`}/>
          <text style={{ font: "30px sans-serif", userSelect: "none" }}
                x={gridToBoardPixelX(x - 1, y + 2)}
                y={gridToBoardPixelY(x - 1, y + 2) - 5}>{name}</text>
        </g>,
      )
    }
  })

  ofType(props.actions, types.ADD_MEDIUM_CITY).forEach(action => {
    const [x, y] = action.data.location
    const name = action.data.name
    citiesElements.unshift(
      <g key={name}>
        <rect x={gridToBoardPixelX(x, y) - spaceBetween * .3}
              y={gridToBoardPixelY(x, y) - spaceBetween * .3} width={spaceBetween * .6} height={spaceBetween * .6}
              style={{ fill: cityFill }}/>
        <text style={{ font: "30px sans-serif", userSelect: "none" }}
              x={gridToBoardPixelX(x - 2, y + 1)}
              y={gridToBoardPixelY(x - 2, y + 1) - 5}>{name}</text>
      </g>)
  })

  ofType(props.actions, types.ADD_SMALL_CITY).forEach(action => {
    const [x, y] = action.data.location
    const name = action.data.name
    citiesElements.unshift(
      <g key={name}>
        <circle cx={gridToBoardPixelX(x, y)}
                cy={gridToBoardPixelY(x, y)} r={spaceBetween * .3}
                style={{ fill: cityFill }}/>
        <text style={{ font: "30px sans-serif", userSelect: "none" }}
              x={gridToBoardPixelX(x - 2, y + 1)}
              y={gridToBoardPixelY(x - 2, y + 1) - 5}>{name}</text>
      </g>)
  })

  return (
    <g>
      {citiesElements}
    </g>
  )
}

export default CitiesLayer