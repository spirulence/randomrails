import React, { useEffect, useState } from "react"
import GoodsLayer from "./boardlayers/goods"
import TrainsLayer from "./boardlayers/trains"
import CitiesLayer from "./boardlayers/cities"
import TrackLayer from "./boardlayers/track"
import { areAdjacent, spaceBetween } from "./boardlayers/common"
import SelectionCircle from "./boardlayers/selection"
import { graphql, useStaticQuery } from "gatsby"


const PlayBoard = (props) => {
  const data = useStaticQuery(graphql`
    query {
      trackCursor: file(relativePath: { eq: "cursors-track.svg" }) {
        publicURL
      }
      trainCursor: file(relativePath: { eq: "cursors-train.svg" }) {
        publicURL
      }
    }`)

  const gameId = props.gameId
  const actions = props.actions
  const setNeedToFetch = props.setNeedToFetch

  const [selected, setSelected] = useState(null)
  const [zoom, setZoom] = useState(1.0)
  const [containerSize, setContainerSize] = useState(null)
  const [viewPoint, setViewPoint] = useState([3500 / 2, 2000 / 2])
  const [mouseDown, setMouseDown] = useState(false)
  const [mouseDownStartingPoint, setMouseDownStartingPoint] = useState({})

  function reportClick(clientX, clientY) {
    const baseImage = document.getElementById("base-image").getBoundingClientRect()

    const boardLeftToViewLeft = baseImage.x
    const boardTopToViewTop = baseImage.y

    const boardUnscaledX = clientX - boardLeftToViewLeft
    const boardUnscaledY = clientY - boardTopToViewTop

    const boardX = boardUnscaledX / zoom
    const boardY = boardUnscaledY / zoom

    const y = Math.round((boardY / spaceBetween) - 0.5)
    let x = Math.round((boardX / spaceBetween) - 0.5)
    if (y % 2 === 1) {
      x = Math.round((boardX / spaceBetween) - 1.0)
    }

    if (selected != null) {
      if (props.inputMode === "move_train") {
        fetch(`/game/${gameId}/actions/move-train/${x}/${y}/`, { method: "POST" }).then(() => {
          setNeedToFetch(true)
        })
      } else if (props.inputMode === "add_track") {
        if (areAdjacent(selected, [x, y])) {
          fetch(`/game/${gameId}/actions/add/track/${x}/${y}/to/${selected[0]}/${selected[1]}/`, { method: "POST" }).then(() => {
            setNeedToFetch(true)
          })
        }
      }
    }

    setSelected([x, y])
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
        mouse: { x: event.screenX, y: event.screenY },
        viewPoint: { x: viewPoint[0], y: viewPoint[1] },
      })
    }}
         onMouseUp={() => {
           setMouseDown(false)
         }}
         onMouseMove={(event) => {
           if (mouseDown) {
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
           onClick={(event) => {
             reportClick(event.clientX, event.clientY)
           }}
           style={{
             position: "fixed",
             top: 0,
             left: 0,
             height: "100%",
             width: "100%",
             cursor: props.inputMode === "add_track" ? `url("${data.trackCursor.publicURL}") 4 2, pointer` : `url("${data.trainCursor.publicURL}") 2 5, default`,
           }}>
        <image id="base-image" href={`/game/${gameId}/map/render`}/>
        <SelectionCircle selected={selected}/>
        <TrackLayer actions={actions}/>
        <CitiesLayer actions={actions}/>
        <GoodsLayer actions={actions}/>
        <TrainsLayer actions={actions}/>
      </svg>
    </div>
  )
}

export default PlayBoard

