import React, { useState } from "react"

const CrayonChooser = (props) => {
  function randomizeCrayon(){
    const red = Math.floor(Math.random()* 200 + 50);
    const green = Math.floor(Math.random()* 200+ 50);
    const blue = Math.floor(Math.random()* 200+ 50);
    props.setCrayon(`rgb(${red},${green},${blue})`)
  }

  if (props.crayon !== null){
    return (
      <div style={{display: "inline-block"}}>
        <button onClick={randomizeCrayon} style={{backgroundColor: props.crayon}}>Switch Crayon</button>
      </div>
    )
  } else {
    return (
      <div style={{display: "inline-block"}}>
        <button onClick={randomizeCrayon}>Grab Crayon</button>
      </div>
    )
  }
}

export default CrayonChooser