import React from "react"


const NotPartOfThisGame = () => {
  return (
    <div style={{ position: "fixed", top: "35%", width: "100%" }}>
      <div style={{ maxWidth: "600px", padding: "5px", margin: "auto" }}>
        <h1>Random Rails</h1>
        <h3>You're not a member of this game yet.</h3>
        <h3>If you think you should be, get in touch with your host and ask for an invite.</h3>
        <h5>Or if this feels like a bug, sorry.</h5>
      </div>
    </div>
  )
}

export default NotPartOfThisGame