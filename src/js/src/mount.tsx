import React from "react";
import { render } from "react-dom";
import { Layout } from "@reactpy/client/src/components";
import { ReactPyDjangoClient } from "./client";

export function mount(element: HTMLElement, client: ReactPyDjangoClient): void {
  const prerenderElement = document.getElementById(element.id + "-prerender");
  if (prerenderElement) {
    element.hidden = true;
    client.onMessage("layout-update", ({ path, model }) => {
      if (prerenderElement) {
        prerenderElement.replaceWith(element);
        element.hidden = false;
      }
    });
  }
  render(<Layout client={client} />, element);
}
