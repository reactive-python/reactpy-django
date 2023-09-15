import React from "react";
import { render } from "react-dom";
import { Layout } from "@reactpy/client/src/components";
import { ReactPyDjangoClient } from "./client";

export function mount(element: HTMLElement, client: ReactPyDjangoClient): void {
  const preloadElement = document.getElementById(element.id + "-preload");
  if (preloadElement) {
    element.hidden = true;
    client.onMessage("layout-update", ({ path, model }) => {
      if (preloadElement) {
        preloadElement.replaceWith(element);
        element.hidden = false;
      }
    });
  }
  render(<Layout client={client} />, element);
}
