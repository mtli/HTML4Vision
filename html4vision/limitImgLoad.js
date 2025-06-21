function limitImgLoad(maxConcurrency) {
    "use strict";
    if (!maxConcurrency || maxConcurrency <= 0) {
        return;
    }

    const maxRetries = 10;
    const baseDelay = 100;

    // Collect images prepared with a "data-src" attribute that holds the real URL.
    // (When the HTML is generated with the concurrency-limit option, <img> tags are
    //  emitted without a "src" so nothing is fetched until we say so.)
    const imgs = Array.from(document.querySelectorAll("img[data-src]"));
    const queue = imgs.map(img => {
        const src = img.getAttribute("data-src");
        return { img, src, retries: 0, delay: baseDelay };
    });

    let active = 0;

    function scheduleNext() {
        while (active < maxConcurrency && queue.length) {
            const item = queue.shift();
            if (item) {
                loadItem(item);
            }
        }
    }

    function loadItem(item) {
        active += 1;

        const { img, src } = item;

        function cleanup() {
            img.removeEventListener("load", onLoad);
            img.removeEventListener("error", onError);
            active -= 1;
            scheduleNext();
        }

        function onLoad() {
            cleanup();
        }

        async function onError() {
            // Try to figure out if this is a rate-limit error.
            let isRateLimited = false;
            try {
                const resp = await fetch(src, { method: "HEAD" });
                isRateLimited = resp.status === 429 || resp.status === 503;
            } catch (e) {
                // Cross-origin or network error - we cannot determine status.
            }

            if (isRateLimited && item.retries < maxRetries) {
                const delay = item.delay;
                // Exponential back-off for subsequent retries
                item.retries += 1;
                item.delay *= 2;
                setTimeout(() => {
                    queue.unshift(item);
                    scheduleNext();
                }, delay);
            } else {
                // Give up - restore the broken image icon.
                img.setAttribute("src", src);
                cleanup();
            }
        }

        img.addEventListener("load", onLoad, { once: true });
        img.addEventListener("error", onError, { once: true });
        // Kick off the actual request.
        img.setAttribute("src", src);
        // Remove the data attribute to avoid re-queuing on retries.
        img.removeAttribute("data-src");
    }

    // Kick things off once the page has finished loading so dimensions are preserved.
    if (document.readyState === "complete") {
        scheduleNext();
    } else {
        window.addEventListener("load", scheduleNext);
    }
} 