import { Component, OnInit, ViewChild, ElementRef, Input, Output, EventEmitter, AfterViewInit } from '@angular/core';
import { TemplateRef } from '@angular/core';

import { HttpClient } from '@angular/common/http';

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
  visibility: boolean = false;

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
    console.log(`Creator: ${this.creator}`)
  }

  private responseTransCreator = (data: any): any => {
    this.trans_creator = data['trans_creator'];
    console.log(`Trans Creator: ${this.trans_creator}`)

    this.card = this.cardContainer.nativeElement;
    // this.width = this.card.parentNode.clientWidth;
    // this.height = this.card.parentNode.clientHeight;
    // this.canva = document.getElementById('cardNodes');
    // this.widthc = this.card.parentNode.clientWidth;
    // this.heightc = this.card.parentNode.clientHeight;

    // console.log(Window.)
    this.innerWidth = this.windowService.nativeWindow.innerWidth - 72;
    this.innerHeight = this.windowService.nativeWindow.innerHeight - 430;
    console.log(`!! Inner Width: ${this.innerWidth}`);
    console.log(`!! Inner Heright: ${this.innerHeight}`);

      // (document.getElementById('cardNodes'))
    // const Graph = ForceGraph3D({ controlType: 'orbit' })
    //   (this.card)
    //     // .jsonUrl('./assets/graph.json')
    //     .graphData(this.trans_creator)
    //     .width(this.width)
    //     .height(this.height)
    //     .nodeLabel('id')
    //     .nodeThreeObject((node: any)  => {
    //       const imgTexture = new THREE.TextureLoader().load(`./assets/images/MAC.png`);
    //       // const imgTexture = new THREE.TextureLoader().load(`./assets/images/${node['type']}.png`);
    //       const material = new THREE.SpriteMaterial({ map: imgTexture });
    //       const sprite = new THREE.Sprite(material);
    //       sprite.scale.set(12, 12, 12);
    //       return sprite;
    //     })
    //     .linkDirectionalArrowLength(3.5)
    //     .linkDirectionalArrowRelPos(1)
    //     .linkCurvature(0.1)
    //     .linkColor(() => 'rgba(255, 163, 102, 1)')
    //     .linkWidth(0.5)
    //     .nodeColor(() => 'rgba(255, 133, 51, 1)')
    //     .backgroundColor('rgba(255, 255, 255, 0)');

    console.log("!! creator", this.creator.wallet);

    // const Graph = ForceGraph3D({
    //   // extraRenderers: [new CSS2DRenderer()]
    //   controlType: 'orbit',
    //   extraRenderers: [(new CSS2DRenderer() as any)]
    // })
    // (this.card)
    //   .graphData(this.trans_creator)
    //   // .nodeThreeObject(node => {

    //   //   //Add background sphere draggable object to node
    //   //   const imgTexture = new THREE.TextureLoader().load(`${node.assetpreview_base64img}`);
    //   //   const material = new THREE.SpriteMaterial({ map: imgTexture });
    //   //   const sprite = new THREE.Sprite(material);
    //   //   sprite.scale.set(12, 12);

    //   //   //Add foreground text label to node
    //   //   let filenameNoExtension = node.assetfile_filename.split(".")[0];
    //   //   const label = new SpriteText("\n" + filenameNoExtension);
    //   //   label.material.depthWrite = false; // make sprite background transparent
    //   //   label.textHeight = 0.3;
    //   //   sprite.add(label)

    //   //   //Return for rendering
    //   //   return sprite;

    //   // })
    //   .nodeThreeObject(node => {

    //     // TODO: Work with type
    //     // console.log(nodo.type);

    //     // Color
    //     if (node.id == this.creator.wallet) {
    //       new THREE.MeshLambertMaterial({
    //         color: Math.round(Math.random() * Math.pow(2, 24)),
    //         transparent: true,
    //         opacity: 0.75
    //       })
    //     }
    //     if (node.id == this.creator.contract) {
    //       new THREE.MeshLambertMaterial({
    //         color: Math.round(Math.random() * Math.pow(2, 24)),
    //         transparent: true,
    //         opacity: 0.75
    //       })
    //     }

    //     const nodeEl = document.createElement('div') as HTMLDivElement;;
    //     nodeEl.textContent = "";
    //     if (typeof node.id === 'string' || typeof node.id === 'number') {
    //       nodeEl.textContent = node.id.toString();
    //     } 
    //     nodeEl.className = 'node-label';
    //     console.log(nodeEl);
    //     return new CSS2DObject(nodeEl);
    //   })
    //   .width(this.innerWidth)
    //   .height(this.innerHeight)
    //   .nodeThreeObjectExtend(true)
    //   // .nodeColor(d => {
    //   //   console.log("node", d)
    //   //   // if (node == "contract") {
    //   //   //   return `rgb(255, 0, 0)`
    //   //   // } else {
    //   //   //   return `rgb(0, 255, 0)`
    //   //   // }
    //   // })     
    //   .linkDirectionalArrowLength(3.5)
    //   .linkDirectionalArrowRelPos(1)
    //   .linkCurvature(0.1)
    //   // .linkColor(() => 'rgba(255, 255, 255, 1)')
    //   .linkColor(link => {
    //     if (link.source == this.creator.wallet) {
    //       return `rgb(255, 0, 0)`
    //     } else {
    //       return `rgb(0, 255, 0)`
    //     }
    //   })
    //   .linkWidth(0.5)
    //   .linkOpacity(0.5)
    //   // .cameraPosition(
    //   //       { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
    //   //       node, // lookAt ({ x, y, z })
    //   //       3000  // ms transition duration
    //   // );
    //   // .cameraPosition({ x: 0, y: 0, z: 0 }, { x: 0, y: 0, z: 1 }, 3000)
    //   .cameraPosition({ x: 0, y: 0, z: -100 })
    //   // .zoomToFit(0, 10, node.id ) 
    //   // .nodeColor(() => 'rgba(255, 133, 51, 1)')
    //   // .zoomToFit(10, 10, node => { 
    //   //   console.log(node);
    //   // })
    //   .backgroundColor('rgba(255, 255, 255, 0)');


    const Graph = ForceGraph3D({ controlType: 'orbit' })
      (this.card)
        // .nodeThreeObject(({ id }) => new THREE.Mesh(
        //   [
        //     new THREE.BoxGeometry(Math.random() * 20, Math.random() * 20, Math.random() * 20),
        //     new THREE.ConeGeometry(Math.random() * 10, Math.random() * 20),
        //     new THREE.CylinderGeometry(Math.random() * 10, Math.random() * 10, Math.random() * 20),
        //     new THREE.DodecahedronGeometry(Math.random() * 10),
        //     new THREE.SphereGeometry(Math.random() * 10),
        //     new THREE.TorusGeometry(Math.random() * 10, Math.random() * 2),
        //     new THREE.TorusKnotGeometry(Math.random() * 10, Math.random() * 2)
        //   ][id%7],
        //   new THREE.MeshLambertMaterial({
        //     color: Math.round(Math.random() * Math.pow(2, 24)),
        //     transparent: true,
        //     opacity: 0.75
        //   })
        // ))
      // .nodeThreeObject( node => new THREE.Mesh(
      //     new THREE.SphereGeometry(5, 5, 5),
      //     new THREE.MeshLambertMaterial({
      //       color: "#66d9ff",
      //       transparent: true,
      //       opacity: 0.75
      //     })
      // ))
      .nodeThreeObject( (node) => {
      // .nodeThreeObject(({ id }) => {
        console.log(node);
        const type = (node as any).type
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
      .cameraPosition({ x: 0, y: 0, z: -250 })
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


  // clicking = (data: any) => {
  //   if (data) {
  //     if (data.name == "IN") {this.onInfo.emit(data.__dataNode.parent.data.name)}
  //     else if (data.name == "OUT") {this.onInfo.emit(data.__dataNode.parent.data.name)}
  //     else {this.onInfo.emit(data.name);}
  //     this.circle1.zoomToNode(data);
  //   } else {
  //     this.circle1.zoomReset();
  //     this.onInfo.emit("null");
  //   }
  // }

}
