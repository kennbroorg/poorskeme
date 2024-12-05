import { Component, OnInit, Output, ViewChild, HostBinding, EventEmitter } from '@angular/core';
import { NbAccordionItemComponent } from '@nebular/theme';
import { NbGlobalLogicalPosition, NbGlobalPhysicalPosition, NbGlobalPosition, NbToastrService, NbIconConfig } from '@nebular/theme';
import { FileUploadValidators } from '@iplab/ngx-file-upload';
import { FormControl, FormGroup } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { SSE } from '../sse/see.service';


@Component({
  selector: 'app-contract-collect',
  templateUrl: './contract-collect.component.html',
  providers: [SSE],
  styleUrls: ['./contract-collect.component.scss']
})
export class ContractCollectComponent implements OnInit {

  @HostBinding('class')
  classes = 'example-items-rows';

  @Output() onProcess: EventEmitter<string> = new EventEmitter<string>();

  // TODO: Remove unnecesary
  // sseSubscription: any;
  sseSubscriptionGet: any;
  // sseSubsChecking: any;
  log: boolean = true;
  logs: string[] = [];
  url: string = "http://127.0.0.1:5000/"

  positions = NbGlobalLogicalPosition;

  // TODO: Remove this variables

  public animation: boolean = false;
  public multiple: boolean = false;

  @ViewChild('internetItem') internetItem!: NbAccordionItemComponent;
  @ViewChild('fileItem') fileItem!: NbAccordionItemComponent;

  private filesControl = new FormControl<File[]>([], FileUploadValidators.filesLimit(2));

  public demoForm = new FormGroup({
      files: this.filesControl
  });

  constructor(private http: HttpClient, private toastrService: NbToastrService, private sse: SSE) { }

  ngOnInit(): void {
    console.log(`Collect Process`);
  }

  public toggleStatus(): void {
      this.filesControl.disabled ? this.filesControl.enable() : this.filesControl.disable();
  }

  public toggleMultiple() {
      this.multiple = !this.multiple;
  }

  public clear(): void {
      this.filesControl.setValue([]);
  }

  showToast(message: string, title: string, iconName: string) {
    const iconConfig: NbIconConfig = { icon: iconName, pack: 'eva' };
    this.toastrService.show(
      title,
      message,
      { limit: 2, position: NbGlobalLogicalPosition.BOTTOM_END, icon: iconConfig, toastClass: 'toast-class', duration: 3000 });
  }

  process(caddress: string, bfrom: string, bto: string) {

    if (this.internetItem.expanded) {
      if (caddress && caddress.trim() !== '') {
        const data = {
          caddress: caddress,
          bfrom: bfrom,
          bto: bto
        };

        this.http.post('http://127.0.0.1:5000/get_data_process', data).subscribe(
          (response) => {
            console.log('Datos procesados exitosamente', response);
            // Aquí puedes manejar la respuesta del backend
          },
          (error) => {
            console.error('Error al procesar los datos', error);
            // Aquí puedes manejar el error
          }
        );
      } else {
        this.showToast('Error', 'Contract Address field must have a value', 'alert-circle-outline')
      }
    } else if (this.fileItem.expanded) {
      const files = this.filesControl.value;
      if (files && files.length > 0) {
        const formData = new FormData();
        formData.append('file', files[0]); // Solo un archivo

        this.http.post('http://127.0.0.1:5000/upload_file', formData).subscribe(
          (response) => {
            const resp: any = response;
            if (resp['status'] === "error") {
              this.showToast('Error', resp['message'], 'alert-circle-outline')
            } else {
              this.logs = [...this.logs, `<strong>UPLOAD</strong> - File uploaded successfully`];

              const file_id = resp['file_id'];
              this.getFileInfo("file_process", { 'file_id': file_id });
              this.onProcess.emit('true');

            }
          },
          (error) => {
            this.showToast('Error', error, 'alert-circle-outline')
          }
        );

      } else {
        this.showToast('Error', 'You must upload a file', 'alert-circle-outline')
      }
    } else {
      this.showToast('Error', 'You must select an option to process data', 'alert-circle-outline')
    }
  }

  getFileInfo(endpoint: string, params: any): void {
    console.log("PARAMS", params);
    this.sseSubscriptionGet = this.sse.observeParam(this.url + endpoint, params).subscribe(d => {
        console.log('DATA', d);
        if (d['end'] == true) {
          this.logs = [...this.logs, d['msg']];
          this.sseSubscriptionGet.unsubscribe();
        } else {
          this.logs = [...this.logs, d['msg']];
          // if (d.hasOwnProperty('content')) {
          //   if (d['content'].hasOwnProperty('wallet_detail')) {
          //     this.processWalletDetail(d['content']['wallet_detail']);
          //   }
          //   if (d['content'].hasOwnProperty('graph')) {
          //     this.processGraph(d['content']['graph']);
          //     console.warn("GRAPH", d['content']['graph']);
          //   }
          //   if (d['content'].hasOwnProperty('list')) {
          //     this.processList(d['content']['list']);
          //   }
          //   if (d['content'].hasOwnProperty('stat')) {
          //     this.stats = d['content']['stat'];
          //   }
          //   if (d['content'].hasOwnProperty('balance')) {
          //     this.processBalance(d['content']['balance']);
          //   }
          //   if (d['content'].hasOwnProperty('gas')) {
          //     this.gas = d['content']['gas'];
          //   }
          //   if (d['content'].hasOwnProperty('tokens')) {
          //     this.tokens = d['content']['tokens'];
          //   }
          //   if (d['content'].hasOwnProperty('tags')) {
          //     this.tags = d['content']['tags'];
          //   }
          //   if (d['content'].hasOwnProperty('labels')) {
          //     this.labels = d['content']['labels'];
          //   }
          //   if (d['content'].hasOwnProperty('funders')) {
          //     this.processFunders(d['content']['funders']);
          //   }
          //   if (d['content'].hasOwnProperty('address')) {
          //     this.address['address'] = d['content']['address'];
          //   }
          //   if (d['content'].hasOwnProperty('addresses')) {
          //     this.address['addresses'] = d['content']['addresses'];
          //   }
          //   if (d['content'].hasOwnProperty('network')) {
          //     this.address['network'] = d['content']['network'];
          //   }
          //   if (d['content'].hasOwnProperty('type')) {
          //     this.address['type'] = d['content']['type'];
          //   }
          //   if (d['content'].hasOwnProperty('filters')) {
          //     this.filters = d['content']['filters'];
          //   }
          // }
        }
      });
  }
}
