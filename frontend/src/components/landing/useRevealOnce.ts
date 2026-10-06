import { useEffect, useRef, useState } from 'react';

/**
 * 'pending' until the element first scrolls into view, then 'done', once. Used for the one
 * piece of landing motion that carries meaning (the evidence line drawing). With reduced motion
 * or no IntersectionObserver it is 'done' from the first render, so nothing is ever hidden.
 */
export function useRevealOnce<T extends HTMLElement>(): [React.RefObject<T | null>, 'pending' | 'done'] {
  const ref = useRef<T | null>(null);
  const [state, setState] = useState<'pending' | 'done'>(() =>
    typeof window === 'undefined'
    || typeof IntersectionObserver === 'undefined'
    || window.matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 'done'
      : 'pending',
  );

  useEffect(() => {
    const el = ref.current;
    if (state === 'done' || !el) return;
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        setState('done');
        observer.disconnect();
      }
    }, { rootMargin: '0px 0px -25% 0px' });
    observer.observe(el);
    return () => observer.disconnect();
  }, [state]);

  return [ref, state];
}
