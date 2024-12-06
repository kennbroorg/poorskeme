import { Component, OnInit, Output, ViewChild, ElementRef, HostBinding, EventEmitter, AfterViewInit, OnChanges, SimpleChanges } from '@angular/core';
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
export class ContractCollectComponent implements OnInit, AfterViewInit, OnChanges {

  @HostBinding('class')
  classes = 'example-items-rows';

  @ViewChild('scrollableCard') private scrollContainer!: ElementRef;
  @Output() onProcess: EventEmitter<string> = new EventEmitter<string>();

  sseSubscriptionGet: any;
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

  ngAfterViewInit() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    console.log("Container", this.scrollContainer);
    try {
      this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    } catch(err) {
      console.error(err);
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    console.log("CHANGES", changes);
    if (changes['logs']) {
      // setTimeout(() => this.scrollToBottom(), 100);
      // console.log("DATA CAMBIO");
      this.scrollToBottom();
    }
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

  process(caddress: string, bfrom: string, bto: string, network: string) {

    if (this.internetItem.expanded) {
      if (caddress && caddress.trim() !== '') {
        const data = {
          caddress: caddress,
          bfrom: bfrom,
          bto: bto,
          network: network
        };

        this.getFileInfo("get_data_process", data);
        this.onProcess.emit('true');

        // this.http.post('http://127.0.0.1:5000/get_data_process', data).subscribe(
        //   (response) => {
        //     console.log('Datos procesados exitosamente', response);
        //   },
        //   (error) => {
        //     this.showToast('Error', error, 'alert-circle-outline')
        //   }
        // );
        //
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
          // }
        }
      });
  }
}
