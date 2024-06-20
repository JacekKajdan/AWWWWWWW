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
                        <rect v-for="r in curPic" :x="r.x" :y="r.y" :width="r.w" :height="r.h" :fill="r.color" />
                    </svg>
                    <v-progress-circular v-else indeterminate color="primary"></v-progress-circular>
                </v-card-text>
                <v-card-actions>
                    <v-btn @click="closeDialog">Zamknij podgląd</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
        <div v-if="nr_new_pics>nr_old_pics">
            <v-chip color="primary" class="ma-2">
            Nowe obrazki!  ({{ (nr_new_pics-nr_old_pics)/10 }})</v-chip>
            <v-btn color="primary" class="ma-2" @click="get_all_pic">Pobierz nowe obrazki</v-btn>

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
            pics: [],
            currentPage: 1,
            pageSize: 3,
            totalPages: 1,
            dialogVisible: false,
            curPic: null,
            loading: false,
            error_on_req: false,
            ws: null,
            nr_new_pics: 0,
            nr_old_pics: 0
        };
    },
    //Przy uruchomieniu
    mounted() {
        this.get_all_pic();
        this.setupWebSocket();
    },

    //Koniec polaczenia z ws
    beforeDestroy() {
        if (this.ws) {
            this.ws.close();
        }
    },

    //Obrazki na danej stronie
    computed: {
        displayedItems() {
            const startIndex = (this.currentPage - 1) * this.pageSize;
            return this.pics.slice(startIndex, startIndex + this.pageSize);
        }
    },


    methods: {
        openDialog(index) {
            this.loading = true
            this.get_pic(index);
            this.dialogVisible = true;

        },

        //Pobranie jednego obrazka z serwera
        async get_pic(index) {
            try {
                const response = await axios.get('http://localhost:8000/pics/' + index.toString(),
                    {
                        method: "GET",
                        mode: "cors",
                        headers: {
                            "Access-Control-Allow-Origin": 'http://127.0.0.1:8080',
                            "Accept": "application/json",
                        },
                    });

                console.log('Pobrano:', response.data);
                this.curPic = response.data;
                this.loading = false

                //Bledne pobranie
                if (this.curPic.length > 1000) {
                    this.curPic = null
                    this.error_on_req = true
                }
            } catch (error) {
                this.error_on_req = true
                console.error('Blad podczas pobierania obrazka:', error);
            }
        },

        //Pobranie wszystkich obrazkow
        async get_all_pic() {
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

                console.log('Pobrano:', response.data);
                this.pics = response.data;
                this.totalPages = Math.ceil(this.pics.length / this.pageSize);
                this.nr_old_pics=this.nr_new_pics
                
            } catch (error) {
                console.error('Blad podczas pobierania wszystkich obrazkow:', error);
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
            this.nr_new_pics = event.data; 
            this.nr_new_pics = JSON.parse(this.nr_new_pics)+1

            if(this.nr_old_pics==0){
                this.nr_old_pics=this.nr_new_pics
            }
            
        };
        this.ws.onopen = () => {
            console.log('WebSocket otwarty');
        };
        this.ws.onclose = () => {
            console.log('WebSocket zamkniety');
        };
        this.ws.onerror = (error) => {
            console.error('Blad przy WebSocket:', error);
        };
        }
    }
};
</script>
