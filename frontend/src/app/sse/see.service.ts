import { Injectable, NgZone } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable()
export class SSE {

    constructor(private zone: NgZone) { }

    observe(sseUrl: string): Observable<any> {
        return new Observable<any>(obs => {
            const source = new EventSource(sseUrl);
            source.onmessage = (e) => {
                const data = JSON.parse(e.data);
                // new scope.$apply
                this.zone.run(() => obs.next(data));
            }
            return () => source.close();
        })
    }

    observeParam(sseUrl: string, params?: any): Observable<any> {
        return new Observable<any>(obs => {

            const url = new URL(sseUrl, window.location.origin);
            if (params) {
                Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
            }

            console.log(url);

            const source = new EventSource(url.toString());
            source.onmessage = (e) => {
                const data = JSON.parse(e.data);
                this.zone.run(() => obs.next(data));
            }
            return () => source.close();
        })
    }
}
