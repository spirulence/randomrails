import React, { useEffect, useState } from "react"
import ColorSelectorSquares from "./lobby/colorselectorsquares"
import base64 from "react-native-base64"

const Lobby = (props) => {
  const [colorOptions, setColorOptions] = useState([
    { color: "#00ffcc", available: false },
    { color: "#0B8A00", available: false },
    { color: "#ffd60f", available: false },
    { color: "#ff775a", available: false },
    { color: "#0000ff", available: false },
    { color: "#bf00ff", available: false },
    { color: "#6c1499", available: false },])
  const [selectedColorIndex, setSelectedColorIndex] = useState(-1)

  useEffect(() => {
    fetch(`/game/${props.gameId}/lobby/colors-available/`)
      .then(response => response.json())
      .then(data => {
        setColorOptions(data.result);
      })
  }, [])

  const joinElements = <div>
    <h3>You've been invited to join a game!</h3>
    <h3>Pick a color and a screen name.</h3>
    <input placeholder={"RailBaronScreenNameYeet"} style={{ display: "block", width: "100%" }}/>
    <ColorSelectorSquares colorOptions={colorOptions} selectedColorIndex={selectedColorIndex} selectColor={setSelectedColorIndex}/>
    <button style={{ display: "block", width: "80%", margin: "auto" }} onClick={() => props.join(colorOptions[selectedColorIndex].color)}>Join</button>
  </div>

  return (
    <div style={{ position: "fixed", top: "35%", width: "100%" }}>
      <div style={{ maxWidth: "600px", padding: "5px", margin: "auto" }}>
        <h1>Random Rails</h1>
        {joinElements}
      </div>
    </div>
  )
}

export default Lobby