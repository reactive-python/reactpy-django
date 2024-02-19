// This file uses ReactPy's layout that can convert a JavaScript file into ReactJS `useEffect` hook
() => {
    // this is run once the script is loaded and each time its content changes
    let el = document.body.querySelector("#django-js-prevent-duplicates-value");
    if (el.dataset.django_js === undefined) {
        el.dataset.django_js = 0;
    }
    el.dataset.django_js = Number(el.dataset.django_js) + 1;
    el.textContent =
        "Currently loaded by " + el.dataset.django_js + " component(s)";
    return () => {
        // this is run when the script is unloaded (i.e. it's removed from the tree) or just before its content changes
        el.dataset.django_js = Number(el.dataset.django_js) - 1;
        el.textContent =
            "Currently loaded by " + el.dataset.django_js + " component(s)";
    };
};
