import { Component, OnInit, ViewChild, ElementRef, AfterViewInit, EventEmitter } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { scaleLinear, scaleTime, scaleBand } from 'd3-scale';
// import { select, event as d3event } from 'd3-selection';
import {
  BaseChartComponent,
  ColorHelper,
  ViewDimensions,
  calculateViewDimensions,
  id, 
  SingleSeries
} from '@swimlane/ngx-charts';
// import { NbDialogService } from '@nebular/theme';
import { Color, ScaleType } from '@swimlane/ngx-charts';

@Component({
  selector: 'app-liq-trans',
  templateUrl: './liq-trans.component.html',
  styleUrls: ['./liq-trans.component.scss']
})
export class LiqTransComponent implements OnInit {

  @ViewChild('timegraph') cardContainer!: ElementRef<HTMLDivElement>;

  liq: any;
  tvd: any;

  autoScale = true;
  valueDomain!: number[];
  xAxis: boolean = true;
  yAxis: boolean = false;
  showXAxisLabel: boolean = false;
  showYAxisLabel: boolean = false;
  xAxisLabel: string = 'yAxisLabel';
  yAxisLabel: string = 'xAxisLabel';
  gradient: boolean = false;
  showGridLines: boolean = true;
  animations: boolean = true;
  noBarWhenZero: boolean = true;

  onFilter = new EventEmitter();

  data: any;

  series : any;
  results : any;
  res_date : any;
  card: any;
  width!: number;
  height!: number;
  view: any = [400, 300];

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

  // colors!: ColorHelper;
  customColors: Color = { domain: ['#D13608', '#D17808'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  colorScheme = {domain: ['#a8385d', '#0000FF']};
  schemeType: string = 'ordinal';
  scheme: string = 'fire';
  colors!: ColorHelper;

  scaleType!: string;
  transform!: string;
  margin: any[] = [0, 0, 20, 20];
    // margin: any[] = [10, 20, 10, 0];
  initialized: boolean = false;
  filterId: any;
  filter: any;
  brush: any;
  large: boolean = false;

  constructor(private httpClient: HttpClient) { 
  }

  ngOnInit(): void {
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

  ngAfterViewInit(): void {
    const elem = this.cardContainer.nativeElement;

    this.width = 450;
    this.height = 300;

  }

  private responseTransInfo = (data: any): any => {
    this.liq = data
    this.res_date = this.TimelineConvert();
    this.update();
  }

  private responseTVD = (data: any): any => {
    this.tvd = data;
    console.log("!!! TVD", this.tvd);
  }

  TimelineConvert(): SingleSeries {
    const res_conv: SingleSeries = [];

    for (const d of this.liq) {
      res_conv.push({
        name: new Date(d.name),
        value: d.value
      });
    }
    return res_conv;
  }

  update(): void {
    this.results = this.res_date;
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

    if (this.large) {
        this.dims['height'] = this.height * 1.6;
        this.dims['width'] = this.width * 1.6;
    } else { 
        this.dims['height'] = this.height - 130;
        this.dims['width'] = this.width - 100;
    }

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

    this.colors = new ColorHelper(this.scheme, ScaleType.Ordinal, domain, this.customColors);
  }

}