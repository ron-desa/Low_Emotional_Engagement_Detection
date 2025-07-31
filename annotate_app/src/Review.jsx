import React, { useState } from "react";
import { useLocation } from "react-router-dom";

export default function Review() {
  const location = useLocation();
  const { name, id } = location.state;

  return (
    <>
      <div>
        Review - {name} - {id}
      </div>
      <h1>TO BE DONE, MAYBE TAKE A USER REVIEW HERE</h1>
    </>
  );
}
