import React, { useEffect, useState } from "react"
import { graphql, useStaticQuery } from "gatsby"
import { default as moji } from "./openmoji"


const PlayBoard = (props) => {
  const data = useStaticQuery(graphql`
    query {
      trackCursor: file(relativePath: { eq: "cursors-track.svg" }) {
        publicURL
      }
      trainCursor: file(relativePath: { eq: "cursors-train.svg" }) {
        publicURL
      }
      goods:  allFile(filter: {relativeDirectory: {eq: "openmoji/openmoji-svg-black"}}) {
        edges {
          node {
            id
            name
            publicURL
          }
        }
      }
    }
  `)


  const goodsIcons = {}
  data.goods.edges.forEach((edge) => {
    goodsIcons[edge.node.name + ".svg"] = edge.node.publicURL
  })

  const goodsNames = {}
  moji.forEach((emoji) => {
    goodsNames[emoji.hexcode + ".svg"] = emoji.annotation
  })

  const spaceBetween = 40
  const radius = 3
  const columns = 87
  const rows = 50

  const gameId = props.gameId
  const actions = props.actions
  const setNeedToFetch = props.setNeedToFetch
  const players = props.players
  const [selected, setSelected] = useState(null)
  const [zoom, setZoom] = useState(1.0)
  const [containerSize, setContainerSize] = useState(null)
  const [viewPoint, setViewPoint] = useState([3500 / 2, 2000 / 2])
  const [mouseDown, setMouseDown] = useState(false);
  const [mouseDownStartingPoint, setMouseDownStartingPoint] = useState({});

  const playerColors = []
  players.forEach((player) => {
    playerColors[player.playerNumber] = player.color
  })

  function reportClick(clientX, clientY) {
    const baseImage = document.getElementById("base-image").getBoundingClientRect();

    const boardLeftToViewLeft = baseImage.x;
    const boardTopToViewTop = baseImage.y;

    const boardUnscaledX = clientX - boardLeftToViewLeft;
    const boardUnscaledY = clientY - boardTopToViewTop;

    const boardX = boardUnscaledX / zoom;
    const boardY = boardUnscaledY / zoom;

    const y = Math.round((boardY / spaceBetween) - 0.5);
    let x = Math.round((boardX / spaceBetween) - 0.5);
    if (y % 2 === 1) {
      x = Math.round((boardX / spaceBetween) - 1.0);
    }

    if (selected != null) {
      if (props.inputMode === "move_train") {
        fetch(`/game/${gameId}/actions/move-train/${x}/${y}`, { method: "POST" }).then(() => {
          setNeedToFetch(true)
        })
      } else if (props.inputMode === "add_track") {
        if (areAdjacent(selected, [x, y])) {
          fetch(`/game/${gameId}/actions/add/track/${x}/${y}/to/${selected[0]}/${selected[1]}`, { method: "POST" }).then(() => {
            setNeedToFetch(true)
          })
        }
      }
    }

    setSelected([x, y])
  }

  function areAdjacent(coordinate1, coordinate2) {
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

  function gridToBoardPixelX(x, y) {
    if (y % 2 === 0) {
      return x * spaceBetween + spaceBetween / 2
    } else {
      return x * spaceBetween + spaceBetween
    }
  }

  function gridToBoardPixelBoth(x, y) {
    return `${gridToBoardPixelX(x, y)} ${gridToBoardPixelY(x, y)}`
  }

  function gridToBoardPixelY(x, y) {
    return y * spaceBetween + spaceBetween / 2
  }

  const selectionCircle = selected !== null ? <g>
    <circle cx={gridToBoardPixelX(selected[0], selected[1])} cy={gridToBoardPixelY(selected[0], selected[1])}
            r={radius * 3} stroke="grey" fill="none"/>
  </g> : <g/>


  const majorCityIndicators = []
  const mediumCityIndicators = []
  const smallCityIndicators = []
  const mountainIndicators = []
  const trackSegments = []
  const trainIndicators = {}

  function addMajorCity(collection, action, index) {
    const [x, y] = action.data.location
    const name = action.data.name
    const goods = action.data.available_goods.map((good, goodIndex) => {
      return <image key={goodIndex} x={gridToBoardPixelX(x - 1 + goodIndex, y - 1)}
                    y={gridToBoardPixelY(x - 1 + goodIndex, y - 1) - 5}
                    width={40} height={40}
                    href={goodsIcons[good]}/>
    })
    if (y % 2 === 0) {
      collection.unshift(
        <g key={index}>
          <path fill={"red"}
                d={`M ${gridToBoardPixelBoth(x - 1, y - 1)} 
      L ${gridToBoardPixelBoth(x, y - 1)} 
      L ${gridToBoardPixelBoth(x + 1, y)}
      L ${gridToBoardPixelBoth(x, y + 1)}
      L ${gridToBoardPixelBoth(x - 1, y + 1)}
      L ${gridToBoardPixelBoth(x - 1, y)}`}/>
          <text style={{ font: "30px sans-serif", userSelect: "none" }}
                x={gridToBoardPixelX(x - 1, y + 2)}
                y={gridToBoardPixelY(x - 1, y + 2) - 5}>{name}</text>
          {goods}
        </g>,
      )
    } else {
      collection.unshift(
        <g key={index}>
          <path fill={"red"}
                d={`M ${gridToBoardPixelBoth(x, y - 1)} 
      L ${gridToBoardPixelBoth(x + 1, y - 1)} 
      L ${gridToBoardPixelBoth(x + 1, y)}
      L ${gridToBoardPixelBoth(x + 1, y + 1)}
      L ${gridToBoardPixelBoth(x, y + 1)}
      L ${gridToBoardPixelBoth(x - 1, y)}`}/>
          <text style={{ font: "30px sans-serif", userSelect: "none" }}
                x={gridToBoardPixelX(x - 1, y + 2)}
                y={gridToBoardPixelY(x - 1, y + 2) - 5}>{name}</text>
          {goods}
        </g>,
      )
    }
  }

  function addMediumCity(collection, action, index) {
    const [x, y] = action.data.location
    const name = action.data.name
    const goods = action.data.available_goods.map((good, goodIndex) => {
      return <image key={goodIndex} x={gridToBoardPixelX(x - 1 + goodIndex, y - 1)}
                    y={gridToBoardPixelY(x - 1 + goodIndex, y - 1) - 5}
                    width={40} height={40}
                    href={goodsIcons[good]}/>
    })

    collection.unshift(
      <g key={index}>
        <rect x={gridToBoardPixelX(x, y) - spaceBetween * .3}
              y={gridToBoardPixelY(x, y) - spaceBetween * .3} width={spaceBetween * .6} height={spaceBetween * .6}
              style={{ fill: "rgb(255,0,0)" }}/>
        <text style={{ font: "30px sans-serif", userSelect: "none" }}
              x={gridToBoardPixelX(x - 2, y + 1)}
              y={gridToBoardPixelY(x - 2, y + 1) - 5}>{name}</text>
        {goods}
      </g>,
    )
  }

  function addSmallCity(collection, action, index) {
    const [x, y] = action.data.location
    const name = action.data.name
    const goods = action.data.available_goods.map((good, goodIndex) => {
      return <image key={goodIndex} x={gridToBoardPixelX(x - 1 + goodIndex, y - 1)}
                    y={gridToBoardPixelY(x - 1 + goodIndex, y - 1) - 5}
                    width={40} height={40}
                    href={goodsIcons[good]}/>
    })
    collection.unshift(
      <g key={index}>
        <circle cx={gridToBoardPixelX(x, y)}
                cy={gridToBoardPixelY(x, y)} r={spaceBetween * .3}
                style={{ fill: "rgb(255,0,0)" }}/>
        <text style={{ font: "30px sans-serif", userSelect: "none" }}
              x={gridToBoardPixelX(x - 2, y + 1)}
              y={gridToBoardPixelY(x - 2, y + 1) - 5}>{name}</text>
        {goods}
      </g>)
  }

  function addMountain(collection, action, index) {
    const mountainSize = spaceBetween / 4
    const [x, y] = action.data.location
    collection.unshift(
      <path key={index} fill={"black"}
            d={`M ${gridToBoardPixelX(x, y)} ${gridToBoardPixelY(x, y) - mountainSize} 
      L ${gridToBoardPixelX(x, y) + mountainSize} ${gridToBoardPixelY(x, y) + mountainSize}
      L ${gridToBoardPixelX(x, y) - mountainSize} ${gridToBoardPixelY(x, y) + mountainSize}`}/>,
    )
  }

  function addTrack(collection, action, index) {
    const [[x1, y1], [x2, y2]] = [action.data.from, action.data.to]
    collection.unshift(<line
      key={index}
      x1={gridToBoardPixelX(x1, y1)} y1={gridToBoardPixelY(x1, y1)}
      x2={gridToBoardPixelX(x2, y2)} y2={gridToBoardPixelY(x2, y2)}
      style={{ stroke: playerColors[action.data.playerNumber], strokeWidth: 4 }}
    />)
  }

  const availableLoads = {}
  const cities = {}

  function addToGoodsCheatSheet(action, i) {
    const cityName = action.data.name
    cities[cityName] = []
    action.data.available_goods.map((good, goodIndex) => {
      let goodsName = goodsNames[good].split(":")[0]
      cities[cityName].unshift(goodsName)
      if (!(goodsName in availableLoads)) {
        availableLoads[goodsName] = []
      }
      availableLoads[goodsName].unshift(cityName)
    })
  }

  function moveTrain(action, i) {
    const train = playerColors[action.data.playerNumber]
    const [x, y] = action.data.to

    trainIndicators[train] = <svg key={i} x={gridToBoardPixelX(x, y) - 60}
                                  y={gridToBoardPixelY(x, y) - 150}>
      <g transform="scale(2,-2) translate(0,-100)" fill={train}>
        <path
          d="M 1.000000 1.500000 L 6.000000 6.500000 L 6.000000 16.500000 L 11.000000 16.500000 L 11.000000 11.500000 L 26.000000 11.500000 L 26.000000 16.500000 L 41.000000 16.500000 L 41.000000 1.500000 L 2.325757 1.500000 Z"
          transform="scale(1.000000,1.000000) translate(4.000000,16.000000)" opacity="1.000000"/>
        <path
          d="M 6.000000 4.000000 C 6.000000 5.380712 4.880712 6.500000 3.500000 6.500000 C 2.119288 6.500000 1.000000 5.380712 1.000000 4.000000 C 1.000000 2.619288 2.119288 1.500000 3.500000 1.500000 C 4.880712 1.500000 6.000000 2.619288 6.000000 4.000000 Z"
          transform="scale(1.000000,1.000000) translate(9.000000,11.000000)" opacity="1.000000"/>
        <path
          d="M 6.000000 4.000000 C 6.000000 5.380712 4.880712 6.500000 3.500000 6.500000 C 2.119288 6.500000 1.000000 5.380712 1.000000 4.000000 C 1.000000 2.619288 2.119288 1.500000 3.500000 1.500000 C 4.880712 1.500000 6.000000 2.619288 6.000000 4.000000 Z"
          transform="scale(1.000000,1.000000) translate(29.000000,11.000000)" opacity="1.000000"/>
        <path
          d="M 6.797190 4.000000 C 6.797190 5.380712 5.677902 6.500000 4.297190 6.500000 C 2.916478 6.500000 1.797190 5.380712 1.797190 4.000000 C 1.797190 2.619288 2.916478 1.500000 4.297190 1.500000 C 5.677902 1.500000 6.797190 2.619288 6.797190 4.000000 Z"
          transform="scale(1.000000,1.000000) translate(34.000000,11.000000)" opacity="1.000000"/>
      </g>
    </svg>
  }

  const rivers = []

  function addRiver(collection, action, i) {
    collection.unshift(<g key={i}>
      <polyline points={action.data.locations.map((l) => {
        return `${gridToBoardPixelX(l[0])}, ${gridToBoardPixelX(l[1])}`
      }).join(",")} style={{ stroke: "#7fecff", strokeWidth: "6px", fill: "none" }}/>
    </g>)
  }

  for (let i = 0; i < actions.length; i++) {
    const action = actions[i]
    if (action.type === "add_major_city") {
      addMajorCity(majorCityIndicators, action, i)
    } else if (action.type === "add_medium_city") {
      addMediumCity(mediumCityIndicators, action, i)
    } else if (action.type === "add_small_city") {
      addSmallCity(smallCityIndicators, action, i)
    } else if (action.type === "add_mountain") {
      addMountain(mountainIndicators, action, i)
    } else if (action.type === "add_track") {
      addTrack(trackSegments, action, i)
    } else if (action.type === "move_train") {
      moveTrain(action, i)
    } else if (action.type === "add_river") {
      addRiver(rivers, action, i)
    }
  }

  useEffect(() => {
    const container = document.getElementById("ui-container")
    setContainerSize([container.clientWidth, container.clientHeight])

    window.addEventListener("resize", () => {
      const container = document.getElementById("ui-container")
      setContainerSize([container.clientWidth, container.clientHeight])
    })
  }, [])

  useEffect(() => {
    if (containerSize !== null) {
      const element = document.getElementById("playboard")
      const left = viewPoint[0] - (containerSize[0] / 2) / zoom
      const top = viewPoint[1] - (containerSize[1] / 2) / zoom

      element.setAttribute("viewBox", `${left} ${top} ${containerSize[0] / zoom} ${containerSize[1] / zoom}`)
    }
  }, [zoom, containerSize, viewPoint])

  return (
    <div onMouseDown={(event) => {
           setMouseDown(true)
           setMouseDownStartingPoint({
             mouse: {x: event.screenX, y: event.screenY},
             viewPoint: {x: viewPoint[0], y: viewPoint[1]}
           });
         }}
         onMouseUp={() => {
           setMouseDown(false)
         }}
         onMouseMove={(event) => {
           if(mouseDown){
             const mouseDeltaX = event.screenX - mouseDownStartingPoint.mouse.x
             const mouseDeltaY = event.screenY - mouseDownStartingPoint.mouse.y
             setViewPoint([mouseDownStartingPoint.viewPoint.x - mouseDeltaX, mouseDownStartingPoint.viewPoint.y - mouseDeltaY])
           }
         }}
         onWheel={(event) => {
           const newZoom = Math.max(Math.min(zoom + event.deltaY * -0.001, 3.5), .1)
           setZoom(newZoom)
         }}
         id="ui-container"
         style={{
           position: "fixed",
           top: 0,
           left: 0,
           height: "100%",
           width: "100%",
         }}>
      {props.children}
      <svg id="playboard"
           onClick={(event) => {reportClick(event.clientX, event.clientY)}}
           style={{
             position: "fixed",
             top: 0,
             left: 0,
             height: "100%",
             width: "100%",
             cursor: props.inputMode === "add_track" ? `url("${data.trackCursor.publicURL}") 4 2, pointer` : `url("${data.trainCursor.publicURL}") 2 5, default`,
           }}>
        <image id="base-image" href={`/game/${gameId}/map/render`}/>
        {selectionCircle}
        <g>
          {trackSegments}
        </g>
        <g>
          {mediumCityIndicators}
        </g>
        <g>
          {majorCityIndicators}
        </g>
        <g>
          {smallCityIndicators}
        </g>
        <g>
          {Object.values(trainIndicators)}
        </g>
        <g>
          {rivers}
        </g>
        {/*<g>*/}
        {/*  {clickPoints}*/}
        {/*</g>*/}
      </svg>
    </div>
  )
}

export default PlayBoard

