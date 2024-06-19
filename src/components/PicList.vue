<template>
    <div>
        <h1>Lista obrazków</h1>
        <ul>
            <li v-for="(item, index) in displayedItems">
                Obrazek {{ index + ((currentPage - 1) * pageSize) }}
                <v-btn @click="openDialog(index + ((currentPage - 1) * pageSize))">Podgląd</v-btn>
                <br><br>
            </li>

        </ul>

        <v-dialog v-model="dialogVisible" max-width="600px">
            <v-card>
                <v-card-title>Podgląd</v-card-title>
                <v-card-text>
                    <div v-if="error_on_req" class="bg-red">ERROR</div>
                    <svg v-else-if="!loading" :width="500" :height="500">
                        <rect v-for="r in svgData" :x="r.x" :y="r.y" :width="r.w" :height="r.h" :fill="r.color" />
                    </svg>
                    <v-progress-circular v-else indeterminate color="primary"></v-progress-circular>
                </v-card-text>
                <v-card-actions>
                    <v-btn @click="closeDialog">Zamknij podgląd</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
        <div v-if="wsData>nr_old_pics">
            <v-chip color="primary" class="ma-2">
            Nowe obrazki!  ({{ (wsData-nr_old_pics)/10 }})</v-chip>
            <v-btn color="primary" class="ma-2" @click="sendRequest">Pobierz nowe obrazki</v-btn>

        </div>
        
        <v-pagination v-model="currentPage" :total-visible="5" :length=totalPages :total="totalPages"
            @input="changePage" />

            
    
    </div>
</template>

<script>
import axios from 'axios';
export default {
    data() {
        return {
            items: [],
            currentPage: 1,
            pageSize: 3, // Number of items per page
            totalPages: 1,
            dialogVisible: false,
            selectedItem: -1,
            svgData: null,
            loading: false,
            error_on_req: false,
            ws: null,
            wsData: 0,
            nr_old_pics: 0
        };
    },
    mounted() {
        this.sendRequest();
        this.setupWebSocket();
    },
    beforeDestroy() {
        if (this.ws) {
            this.ws.close();
        }
    },
    computed: {
        displayedItems() {
            const startIndex = (this.currentPage - 1) * this.pageSize;
            return this.items.slice(startIndex, startIndex + this.pageSize);
        }
    },
    methods: {
        openDialog(index) {
            this.selectedItem = index;
            this.loading = true
            this.fetchSVGData(index);
            this.dialogVisible = true;

        },
        async fetchSVGData(index) {
            try {
                // Example: Sending a POST request to FastAPI with requestData
                const response = await axios.get('http://localhost:8000/pics/' + index.toString(),
                    {
                        method: "GET",
                        mode: "cors",
                        headers: {
                            "Access-Control-Allow-Origin": 'http://127.0.0.1:8080',
                            "Accept": "application/json",
                        },
                    });
                console.log('Request sent successfully:', response.data);
                this.svgData = response.data;
                this.loading = false
                if (this.svgData.length > 1000) {
                    this.svgData = null
                    this.error_on_req = true
                }
            } catch (error) {
                this.error_on_req = true
                console.error('Error sending request:', error);
            }
        },
        async sendRequest() {
            try {
                const response = await axios.get('http://127.0.0.1:8000/get_all_pics/',
                    {
                        method: "GET",
                        mode: "cors",
                        headers: {
                            "Access-Control-Allow-Origin": 'http://127.0.0.1:8080',
                            "Accept": "application/json",
                        },
                    }
                );
                this.items = response.data;
                this.totalPages = Math.ceil(this.items.length / this.pageSize);
                this.nr_old_pics=this.wsData
                
            } catch (error) {
                console.error('Error fetching items:', error);
            }
        },
        closeDialog() {
            this.dialogVisible = false;
            this.error_on_req = false;
        },
        changePage(page) {
            this.currentPage = page;
        },

        setupWebSocket() {
        this.ws = new WebSocket('ws://localhost:8000/ws2');
        this.ws.onmessage = (event) => {
            this.wsData = event.data; 
            this.wsData = JSON.parse(this.wsData)+1
            if(this.nr_old_pics==0){
                this.nr_old_pics=this.wsData
            }
            console.log(this.wsData)
            console.log(this.nr_old_pics)
            
        };
        this.ws.onopen = () => {
            console.log('WebSocket connection opened');
        };
        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
        };
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        }
    }
};
</script>

<style>
/* Add your component's styles here */
</style>