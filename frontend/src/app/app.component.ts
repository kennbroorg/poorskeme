import { Component } from '@angular/core';
import { Subject } from "rxjs";
import { HttpClient } from '@angular/common/http';

import * as d3 from 'd3';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  subject = new Subject<string>();
  selected = false;
  height = 0;
  width = 0;
  contract: any;
  data: any

  constructor(private httpClient: HttpClient) {}

  ngOnInit(): void {
    this.subject.subscribe((text: string) => {
      console.log(`Received from child component: ${text}`);
    });

    var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    this.width = w / 2 - 60;
    this.height =  h - 102;
    // console.log(`h: ${this.height} - w: ${this.width}`)

    const url = "http://127.0.0.1:5000/contract"
    this.httpClient
      .get(url)
      .subscribe(this.responseContract,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Contract Info'),
      );
  }

  handleInfo = (info: string) => {
    this.subject.next(info);

    // console.log(`Info: ${info}`);
    if (info == "null") {
      this.selected = false;
    } else {
      this.selected = true;
    }
  };

  private responseContract = (data: any): any => {
    this.contract = data
    console.log("APP", this.contract);
    // this.trx = [{"name": "IN", "value": this.contract["trx_in"]}, {"name": "OUT", "value": this.contract["trx_out"]}]
    // this.volume = [{"name": "Volume", "value": this.contract["volume"]}]
    // this.wallets = [{"name": "Wallets", "value": this.contract["wallets"]}]
    // this.max_liq = [{"name": "Max Liquidity - " + this.contract['max_liq_date'], "value": this.contract["max_liq"]}]
    // this.cardNumber = [{"name": "Wallets", "value": this.contract["wallets"]}, 
    //                    {"name": "Max Liquidity", "value": this.contract["max_liq"]}]
    // this.code = this.contract['SourceCode']
  }

}
