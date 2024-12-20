<template>
    <div>
        <div id="kakaoMap"></div>
    </div>
</template>

<script>
    export default {
        props: {
            locations: {
                type: Array,
                required: true,
            },
            mapType: {
                type: String,
                default: 'A'
            }
        },
        data () {
            return {
                map : null,
                mapHeight: '80vh'
            }
        },
        mounted() {
            this.mapHeight = this.mapType === 'A' ? '80vh' : '40vh';
            if (this.mapType === 'A') {
                this._initializeKakaoMap_fullview();
            } else {
                this._initializeKakaoMap_spotview();
            }
        },
        methods: {
            _initializeKakaoMap_fullview() {
                try {
                    const script = document.createElement("script");
                    const key = process.env.VUE_APP_KAKAO_API_KEY
                    
                    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${key}&libraries=clusterer`;
                    document.head.appendChild(script);

                    script.onload = () => { 
                        kakao.maps.load(() => {
                            var container = document.getElementById('kakaoMap');
                            var options = {
                                center: new kakao.maps.LatLng(36.0, 128.0),
                                level: 15
                            };
                            var map = new kakao.maps.Map(container, options);

                            var clusterer = new kakao.maps.MarkerClusterer({
                                map: map,
                                averageCenter: true,
                                minLevel: 10
                            });

                            var markers = this.locations.map(location => {
                                return new kakao.maps.Marker({
                                    position: new kakao.maps.LatLng(
                                        parseFloat(location.latitude),
                                        parseFloat(location.longitude)
                                    ),
                                });
                            });

                            clusterer.addMarkers(markers);
                        });
                    };
                } catch (error) {
                    alert("Maps A:" + error.message);
                } finally {
                    console.log("load KAKAOmap A");
                }
            },
            _initializeKakaoMap_spotview() {
                try {
                    const script = document.createElement("script");
                    const key = process.env.VUE_APP_KAKAO_API_KEY
                    
                    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${key}`;
                    document.head.appendChild(script);

                    script.onload = () => { 
                        kakao.maps.load(() => {
                            var container = document.getElementById('kakaoMap'); // 지도를 표시할 div 
                            var option = { 
                                center: new kakao.maps.LatLng(
                                    parseFloat(this.locations[0].latitude),
                                    parseFloat(this.locations[0].longitude)
                                ), // 지도의 중심좌표
                                level: 5 // 지도의 확대 레벨
                            };

                            // 지도 객체를 컴포넌트의 data에 저장
                            var map = new kakao.maps.Map(container, option);

                            var marker = new kakao.maps.Marker({
                                    position: new kakao.maps.LatLng(
                                        parseFloat(this.locations[0].latitude),
                                        parseFloat(this.locations[0].longitude)
                                    ),
                                });
                                // 각 마커를 지도에 표시
                            marker.setMap(map);
                            });
                        }
                    
                } catch (error) {
                    alert("Maps B:" + error.message);
                } finally {
                    console.log("load KAKAOmap B");
                }
            }
        }
    }
</script>

<style scoped>
    #kakaoMap {
        width: 100%;
        height: v-bind(mapHeight);
        margin: 0px auto;
        display: block;
    } 
</style>