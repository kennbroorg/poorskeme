import { Component, OnInit, Input, EventEmitter, ElementRef, ViewChild } from '@angular/core';
import { Color, ScaleType } from '@swimlane/ngx-charts';
import { HttpClient } from '@angular/common/http';
import { scaleLinear, scaleTime, scaleBand } from 'd3-scale';
// import { select, event as d3event } from 'd3-selection';

// import { LegendPosition } from '@swimlane/ngx-charts/lib/common/types/legend.model';
import { LegendPosition } from '@swimlane/ngx-charts';

import { brushX } from 'd3-brush';
import { select } from 'd3-selection';

import {
  BaseChartComponent,
  ColorHelper,
  ViewDimensions,
  calculateViewDimensions,
  id, 
  SingleSeries
} from '@swimlane/ngx-charts';
// import { NbDialogService } from '@nebular/theme';

// import * as d3 from "d3";

@Component({
  selector: 'app-contract-detail',
  templateUrl: './contract-detail.component.html',
  styleUrls: ['./contract-detail.component.scss']
})
export class ContractDetailComponent implements OnInit {

  @ViewChild('timegraph') cardContainer!: ElementRef<HTMLDivElement>;
  @Input() public data: any;

  contract: any;
  view: any = [500, 340];
  // view2: any = [500, 200];

  colorScheme: Color = { domain: ['#CCF2FF', '#66D9FF'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  colorSchemeLiq: Color = { domain: ['#66D9FF'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  // colorSchemeI: Color = { domain: ['#D17808'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  colorSchemeTree: Color = { domain: ['#CCF2FF', '#66D9FF', '#00ACE6', '#006080'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  // cardColor: string = 'rgba(0, 0, 0, 0.1)';
  schemeType: string = 'ordinal';
  scheme: string = 'aqua';
  colors!: ColorHelper;

  trx: any = [];
  // volume: any = [];
  // wallets: any = [];
  max_liq_num: number = 0;
  // cardNumber: any = [];
  // innerPadding : any = [0, 0, 0, 0];
  // highlightedCode : any;
  // codeRaw : any;

  // currentTheme: string = themeHL;

  liq: any;
  liq_date: any;
  tvd_date: any;

  autoScale = false;
  valueDomain!: number[];
  xAxis: boolean = false;
  yAxis: boolean = true;
  showXAxisLabel: boolean = true;
  showYAxisLabel: boolean = true;
  xAxisLabel: string = 'Date';
  yAxisLabel: string = 'Assets';
  gradient: boolean = true;
  showGridLines: boolean = false;
  animations: boolean = true;
  noBarWhenZero: boolean = true;
  roundDomains: boolean = true;
  showLegend: boolean = false;
  legendOptions: boolean = false;

  onFilter = new EventEmitter();

  // data: any;

  series : any;
  results : any;
  res_date : any;
  card: any;
  // width!: number;
  // height!: number;
  width: number = 900;
  height: number = 300;
  viewIO: any = [900, 300];
  viewLiq: any = [700, 270];

  dims!: ViewDimensions;
  xSet: any;
  xDomain: any;
  yDomain: any;
  seriesDomain: any;
  yScale: any;
  xScale: any;
  xAxisHeight: number = 0;
  yAxisWidth: number = 0;
  timeScale: any;

  scaleType!: string;
  transform!: string;
  margin: any[] = [0, 0, 20, 20];
    // margin: any[] = [10, 20, 10, 0];
  initialized: boolean = false;
  filterId: any;
  filter: any;
  brush: any;
  large: boolean = false;
  // legendPosition = LegendPosition.Right;
  public legendPosition: LegendPosition = LegendPosition.Right;

  // constructor(private httpClient: HttpClient, 
  //             private dialogService: NbDialogService,
  //             private hljsLoader: HighlightLoader) { 
  // }

  constructor(private httpClient: HttpClient) { 
  }

  ngOnInit(): void {
    this.contract = this.data;
    console.log(`Contract : {this.contract}`, this.data);
    this.max_liq_num = Number((this.contract['max_liq']).toFixed(2));
    this.trx = [{"name": "IN", "value": this.contract["trx_in"]}, {"name": "OUT", "value": this.contract["trx_out"]}]
    // this.volume = [{"name": "Volume", "value": this.contract["volume"]}]
    // this.wallets = [{"name": "Wallets", "value": this.contract["wallets"]}]
    // this.max_liq_num = [{"name": "Max Liquidity - " + this.contract['max_liq_date'], "value": this.contract["max_liq"]}]
    // this.cardNumber = [{"name": "Wallets", "value": this.contract["wallets"]}, 
    //                    {"name": "Max Liquidity", "value": this.contract["max_liq"]}]
    // this.code = this.contract['SourceCode']

    const url = "http://127.0.0.1:5000/liq"
    this.httpClient
      .get(url)
      .subscribe(this.responseTransInfo,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Transaction Info'),
      );
    const url_2 = "http://127.0.0.1:5000/tvd"
    this.httpClient
      .get(url_2)
      .subscribe(this.responseTVD,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Transaction Info'),
      );
  }

  private responseTransInfo = (data: any): any => {
    this.liq = data
    this.liq_date = this.TimelineConvert(this.liq);
    // this.results = [this.liq];
    this.results = [{'name': '', 'series': this.liq_date}];
    // this.update();
    console.log("!!! LIQ", this.liq);
    console.log("!!! DATE", this.liq_date);
  }

  private responseTVD = (data: any): any => {
    this.tvd_date = data;
    this.res_date = this.TimelineConvert(this.tvd_date[0]['series']);
    this.tvd_date[0]['series'] = this.res_date;
    this.res_date = this.TimelineConvert(this.tvd_date[1]['series']);
    this.tvd_date[1]['series'] = this.res_date;
    console.log("!!! TVD", this.tvd_date);
  }

  TimelineConvert(serie: any): SingleSeries {
    const res_conv: SingleSeries = [];

    for (const d of serie) {
      res_conv.push({
        name: new Date(d.name),
        value: d.value
      });
    }
    return res_conv;
  }

  update(): void {
    // this.results = this.liq;
    this.dims = calculateViewDimensions({
      width: this.width,
      height: this.height,
      margins: this.margin,
      showXAxis: this.xAxis,
      showYAxis: this.yAxis,
      xAxisHeight: this.xAxisHeight,
      yAxisWidth: this.yAxisWidth,
      showXLabel: this.showXAxisLabel,
      showYLabel: this.showYAxisLabel,
      showLegend: false,
    });
    console.log("DIM", this.dims);

    this.dims['height'] = this.height - 20;
    this.dims['width'] = this.width - 150;

    // if (this.large) {
    //     this.dims['height'] = this.height * 1.6;
    //     this.dims['width'] = this.width * 1.6;
    // } else { 
    //     this.dims['height'] = this.height - 130;
    //     this.dims['width'] = this.width - 100;
    // }

    this.xDomain = this.getXDomain();

    this.yDomain = this.getYDomain();
    this.timeScale = this.getTimeScale(this.xDomain, this.dims.width);
    this.xScale = this.getXScale(this.xSet, this.dims.width);
    this.yScale = this.getYScale(this.yDomain, this.dims.height);

    this.setColors();
    this.transform = `translate(${this.dims.xOffset} , ${this.margin[0]})`;

    if (!this.initialized) {
      // this.addBrush();
      this.initialized = true;
    }
  }

  getXDomain(): any[] {
    const values: any = [];

    for (const d of this.results) {
      if (!values.includes(d.name)) {
        values.push(d.name);
      }
    }

    this.scaleType = this.getScaleType(values);
    let domain = [];

    const min = new Date(Math.min(...values));
    min.setHours(0);
    min.setMinutes(0);
    min.setSeconds(0);

    const max = new Date(Math.max(...values));
    max.setHours(23);
    max.setMinutes(59);
    max.setSeconds(59);

    domain = [min.getTime(), max.getTime()];

    this.xSet = values;
    return domain;
  }

  getYDomain(): any[] {
    if (this.valueDomain) {
      return this.valueDomain;
    }

    const domain = [];

    for (const d of this.results) {
      if (domain.indexOf(d.value) < 0) {
        domain.push(d.value);
      }
      if (d.min !== undefined) {
        if (domain.indexOf(d.min) < 0) {
          domain.push(d.min);
        }
      }
      if (d.max !== undefined) {
        if (domain.indexOf(d.max) < 0) {
          domain.push(d.max);
        }
      }
    }

    let min = Math.min(...domain);
    const max = Math.max(...domain);
    if (!this.autoScale) {
      min = Math.min(0, min);
    }

    return [min, max];
  }

  getXScale(domain: any, width: any): any {
    return scaleBand().range([0, width]).paddingInner(0.1).domain(domain);
  }

  getTimeScale(domain: any, width: any): any {
    return scaleTime().range([0, width]).domain(domain);
  }

  getYScale(domain: any, height: any): any {
    const scale = scaleLinear().range([height, 0]).domain(domain);

    return scale;
  }

  getScaleType(values: any): string {
    return 'time';
  }

  trackBy(index: any, item: any): string {
    return item.name;
  }

  setColors(): void {
    let domain;
    if (this.schemeType === 'ordinal') {
      domain = this.xSet;
    } else {
      domain = this.yDomain;
    }

    this.colors = new ColorHelper(this.scheme, ScaleType.Ordinal, domain, this.colorScheme);
  }
}
