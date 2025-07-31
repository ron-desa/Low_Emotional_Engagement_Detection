import React from "react";
import Navbar from "react-bootstrap/Navbar";

export default function NavbarComponent({ page }) {
  return (
    <Navbar>
      <Navbar.Brand href="/">Annotation App</Navbar.Brand>
      <Navbar.Toggle />
      <Navbar.Collapse className="justify-content-end">
        <Navbar.Text>
          Currently in <b>{page}</b>
        </Navbar.Text>
      </Navbar.Collapse>
    </Navbar>
  );
}
