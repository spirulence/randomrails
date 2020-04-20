import React, { useEffect, useState } from "react"
import GoodsLayer from "./boardlayers/goods"
import TrainsLayer from "./boardlayers/trains"
import CitiesLayer from "./boardlayers/cities"
import TrackLayer from "./boardlayers/track"
import HighlightsLayer from "./boardlayers/highlights"
import { areAdjacent, spaceBetween } from "./boardlayers/common"
import SelectionCircle from "./boardlayers/selection"
import { graphql, useStaticQuery } from "gatsby"
import CountriesLayer from "./boardlayers/countries"


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
  const highlightGood = props.highlightGood
  const highlightCity = props.highlightCity
  const inputMode = props.inputMode

  const [selected, setSelected] = useState(null)
  const [zoom, setZoom] = useState(1.0)
  const [containerSize, setContainerSize] = useState(null)
  const [viewPoint, setViewPoint] = useState([3500 / 2, 2000 / 2])
  const [scroll, setScroll]  = useState(null)

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
      } else if (props.inputMode === "erase_track") {
        if (areAdjacent(selected, [x, y])) {
          fetch(`/game/${gameId}/actions/erase/track/${x}/${y}/to/${selected[0]}/${selected[1]}/`, { method: "POST" }).then(() => {
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

  useEffect(() => {
    const timeout = setInterval(() => {
      if (scroll !== null) {
        setViewPoint([viewPoint[0] + scroll.x, viewPoint[1] + scroll.y])
      }
    }, 25)
    return () => {clearInterval(timeout)}
  }, [viewPoint, scroll])

  const cursors = {
    "add_track": `url("${data.trackCursor.publicURL}") 4 2, pointer`,
    "move_train": `url("${data.trainCursor.publicURL}") 2 5, default`
  }

  return (
    <div id="ui-container" tabIndex={1}
         onKeyDown={(event) => {
           if (event.keyCode === 37) {
             setScroll({ x: -20, y: 0 })
           }else if(event.keyCode === 39){
             setScroll({ x: 20, y: 0 })
           }else if (event.keyCode === 38) {
             setScroll({ x: 0, y: -20 })
           }else if(event.keyCode === 40){
             setScroll({ x: 0, y: 20 })
           }
         }}
         onKeyUp={() => {
           setScroll(null)
         }}
         onWheel={(event) => {
           const newZoom = Math.max(Math.min(zoom + event.deltaY * -0.001, 3.5), .1)
           setZoom(newZoom)
         }}
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
             cursor: props.inputMode in cursors ? cursors[props.inputMode] : `default`,
           }}>
        <image id="base-image" href={`/game/${gameId}/map/render`}/>
        <CountriesLayer actions={actions}/>
        <SelectionCircle selected={selected}/>
        <TrackLayer actions={actions}/>
        <CitiesLayer actions={actions}/>
        <GoodsLayer actions={actions}/>
        <TrainsLayer actions={actions}/>
        <HighlightsLayer actions={actions} gameId={gameId} highlightCity={highlightCity} highlightGood={highlightGood} highlightMovement={inputMode === "move_train"}/>
      </svg>
    </div>
  )
}

export default PlayBoard

