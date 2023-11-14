import { Component, OnInit, ViewChild, ElementRef, Input, Output, EventEmitter, AfterViewInit } from '@angular/core';
import { TemplateRef } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { ColumnMode } from '@swimlane/ngx-datatable';

import ForceGraph3D from '3d-force-graph';
import SpriteText from 'three-spritetext';
import * as THREE from "three";
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';

import { WindowService } from '../service/windows.service';

// import CirclePack from 'circlepack-chart';
@Component({
  selector: 'app-creator',
  templateUrl: './creator.component.html',
  styleUrls: ['./creator.component.scss']
})
export class CreatorComponent implements OnInit {
  @ViewChild('cardNodes', {static: true}) cardContainer!: ElementRef<HTMLElement>;

  canva: any;
  card: any;
  width: any = 500;
  height: any = 500;
  widthc: any;
  heightc: any;
  innerWidth: number;
  innerHeight: number;

  creator: any = [];
  trans_creator: any = [];
  balances: any = [];
  contracts: any = [];
  st: any = [];
  visibility: boolean = false;
  ColumnMode = ColumnMode;
  li: boolean = true;

  dWallet: string = "";
  dType: string = "";
  dValueIN: string = "";
  dValueOUT: string = "";
  dQtyIN: string = "";
  dQtyOUT: string = "";
  dSymbol: string = "";
  dTRX: string = "";
  dToken: string = "";

  constructor(private httpClient: HttpClient, 
              private windowService: WindowService) { }

  ngOnInit(): void {
    console.log("Init de Creator");
  }

  ngAfterViewInit() {
    console.log("AfterInit de Creator");
    const url = "http://127.0.0.1:5000/creator"
    this.httpClient
      .get(url)
      .subscribe(this.responseCreator,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Creator'),
      );

    const url_trans = "http://127.0.0.1:5000/trans_creator"
    this.httpClient
      .get(url_trans)
      .subscribe(this.responseTransCreator,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Creator'),
      );

  }

  private responseCreator = (data: any): any => {
    this.creator = data['creator'];
    this.balances = data['balances'];
    this.contracts = data['contracts'];
    // console.log(`Creator: ${this.creator}`)
  }

  private responseTransCreator = (data: any): any => {
    this.trans_creator = data['trans_creator'];
    this.st = data['stat'];
    // console.log(`Trans Creator: ${this.trans_creator}`)

    this.card = this.cardContainer.nativeElement;

    // console.log(Window.)
    this.innerWidth = this.windowService.nativeWindow.innerWidth - 72;
    this.innerHeight = this.windowService.nativeWindow.innerHeight - 430;
    // console.log(`!! Inner Width: ${this.innerWidth}`);
    // console.log(`!! Inner Heright: ${this.innerHeight}`);


    const Graph = ForceGraph3D({ controlType: 'orbit' })
      (this.card)
      .nodeThreeObject( (node) => {
        const type = (node as any).type
        const tag = (node as any).tag
        if (type === "creator") {
          return new THREE.Mesh(
            new THREE.DodecahedronGeometry(7),
            new THREE.MeshLambertMaterial({
              color: "#66d9ff",
              transparent: true,
              opacity: 0.9
            }));
        } else if (type === "contract") {
          return new THREE.Mesh(
            new THREE.BoxGeometry(7, 7, 7),
            new THREE.MeshLambertMaterial({
              color: "#ffffff",
              transparent: true,
              opacity: 0.75
            }));
        } else if (tag === "Contract Created") {
          return new THREE.Mesh(
            new THREE.BoxGeometry(7, 7, 7),
            new THREE.MeshLambertMaterial({
              color: "#888888",
              transparent: true,
              opacity: 0.75
            }));
        } else if (tag === "Contract") {
          return new THREE.Mesh(
            new THREE.OctahedronGeometry(7, 0),
            new THREE.MeshLambertMaterial({
              color: "#00ace6",
              transparent: true,
              opacity: 0.75
            }));
        } else {
          return new THREE.Mesh(
            new THREE.SphereGeometry(5, 15, 15),
            new THREE.MeshLambertMaterial({
              color: "#66d9ff",
              transparent: true,
              opacity: 0.5
            }));
        }

      })
      .linkColor(link => {
        if (link.source == this.creator.wallet) {
          return `rgb(102, 217, 255)`
        } else {
          return `rgb(204, 242, 255)`
        }
      })
      .width(this.innerWidth)
      .height(this.innerHeight)
      // .nodeThreeObjectExtend(true)
      .nodeLabel(node => {
        const id = (node as any).address.slice(0, 15);
        const type = (node as any).type;
        const trx = (node as any).trx;
        const token = (node as any).token;
        return `
          <div class="node-label">
            ${trx} - Token: ${token}<br>
            ${type}: ${id}...
          </div>
        `
      })
      // .nodeLabel("id")
      // .nodeLabel( () => {
      //   console.log(id);
      // })
      .linkLabel(link => {
        const value = (link as any).value;
        const qty = (link as any).qty;
        return `
          <div class="node-label">
            Value: ${value}<br> 
            Qty: ${qty}
          </div>
        `
      })
      .linkWidth(0.3)
      .linkOpacity(0.5)
      .linkDirectionalArrowLength(3.5)
      .linkDirectionalArrowRelPos(1)
      .linkCurvature(0.1)
      .graphData(this.trans_creator)
      // .d3Force('charge', null)
      // .d3Force('charge', () => { return 100; })
      // .dagMode('radialout')
      // .dagLevelDistance(150)
      .cameraPosition({ x: 0, y: 0, z: -650 })
      .onNodeClick(node => {
        // console.log(node);
        // console.log((node as any).type);
        let x = (node as any).x
        let y = (node as any).y
        let z = (node as any).z
        // Aim at node from outside it
        const distance = -60;
        const distRatio = 1 + distance/Math.hypot(x, y, z);

        const newPos = x || y || z
          ? { x: x * distRatio, y: y * distRatio, z: z * distRatio }
          : { x: 0, y: 0, z: distance }; // special case if node is in (0,0,0)

        Graph.cameraPosition(
          newPos, // new position
          ({ x: x, y: y, z: z }), // lookAt ({ x, y, z })
          3000  // ms transition duration
        );

        // Graph.d3Force('charge').distanceMin(100);

        // Description
        this.dWallet = (node as any).address;
        this.dType = (node as any).type;
        this.dValueIN = (node as any).trx_in;
        this.dValueOUT = (node as any).trx_out;
        this.dQtyIN = (node as any).qty_in;
        this.dQtyOUT = (node as any).qty_out;
        this.dTRX = (node as any).trx;
        this.dToken = (node as any).token;

      })
      .backgroundColor('rgba(255, 255, 255, 0)');
  }

}
