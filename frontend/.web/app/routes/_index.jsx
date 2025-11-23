import {Fragment,useCallback,useContext,useEffect,useRef} from "react"
import {Activity as LucideActivity,ArrowRight as LucideArrowRight,Briefcase as LucideBriefcase,Camera as LucideCamera,CheckCheck as LucideCheckCheck,ChevronDown as LucideChevronDown,FileImage as LucideFileImage,Fuel as LucideFuel,Hexagon as LucideHexagon,History as LucideHistory,Image as LucideImage,LayoutDashboard as LucideLayoutDashboard,MapPin as LucideMapPin,Settings as LucideSettings,UserPen as LucideUserPen,Users as LucideUsers,Wallet as LucideWallet,X as LucideX} from "lucide-react"
import {EventLoopContext,StateContexts,UploadFilesContext} from "$/utils/context"
import {ReflexEvent,isTrue,refs} from "$/utils/state"
import {} from "react-dropzone"
import {Box as RadixThemesBox} from "@radix-ui/themes"
import {useDropzone} from "react-dropzone"
import {jsx} from "@emotion/react"




function Input_30e8b2c09102647e17e5d18b207b155d () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_3b94802b07f4cc443e441e2136493690 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.set_worker_mode", ({ ["is_worker"] : _e?.["target"]?.["checked"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx("input",{className:"sr-only peer",defaultChecked:!(reflex___state____state__app___states___global_state____global_state.user_mode_rx_state_),onChange:on_change_3b94802b07f4cc443e441e2136493690,type:"checkbox"},)
  )
}


function Select_82772b3edf0af23a4040bea5c09aaeb0 () {
  const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_979551502c7e8d7805b5958b59831143 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.set_current_user", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx("select",{className:"w-full bg-slate-900/50 border border-slate-700 text-slate-300 text-sm rounded-lg focus:ring-cyan-500 focus:border-cyan-500 block w-full pl-10 p-2.5 appearance-none cursor-pointer hover:border-cyan-500/50 transition-colors",onChange:on_change_979551502c7e8d7805b5958b59831143},jsx("option",{disabled:true,selected:true,value:""},"Select Wallet"),jsx("option",{value:"Alice"},"Alice"),jsx("option",{value:"Bob"},"Bob"))
  )
}


function P_120831e6cc8fabf0065a61158699a766 () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)



  return (
    jsx("p",{className:"text-sm font-medium text-slate-200"},reflex___state____state__app___states___global_state____global_state.mode_label_rx_state_)
  )
}


function Textarea_26812b47176d76f011cab4809bd18a48 () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_826b2b0382d81bc1831bfe1c47ac2c93 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.set_job_description", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx("textarea",{className:"w-full bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-slate-200 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none min-h-[200px] transition-all placeholder:text-slate-600 font-mono text-sm",defaultValue:reflex___state____state__app___states___global_state____global_state.job_description_rx_state_,onChange:on_change_826b2b0382d81bc1831bfe1c47ac2c93,placeholder:"Describe your task details, requirements, and reward (e.g., 'Validate transaction #1234 - 0.5 ETH')..."},)
  )
}


function Comp_cd734d163e48637b3f590d12c95f5cd7 () {
  const ref_job_images_upload = useRef(null); refs["ref_job_images_upload"] = ref_job_images_upload;
const [addEvents, connectErrors] = useContext(EventLoopContext);
const on_drop_20b2deb76b8f31203f8afc1fc0fc2107 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.auto_upload_files", ({ ["files"] : _ev_0, ["upload_id"] : "job_images_upload", ["extra_headers"] : ({  }) }), ({  }), "uploadFiles"))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const on_drop_rejected_2fcedbdc0771e7617b4270e2d1ac8cc9 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("_call_function", ({ ["function"] : (() => (refs['__toast']?.["error"]("", ({ ["title"] : "Files not Accepted", ["description"] : _ev_0.map(((osizayzf) => (osizayzf?.["file"]?.["path"]+": "+osizayzf?.["errors"].map(((wnkiegyk) => wnkiegyk?.["message"])).join(", ")))).join("\n\n"), ["closeButton"] : true, ["style"] : ({ ["whiteSpace"] : "pre-line" }) })))), ["callback"] : null }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const { getRootProps: xdvxrcsn, getInputProps: udaxihhe, isDragActive: bacghqta} = useDropzone(({ ["accept"] : ({ ["image/png"] : [".png"], ["image/jpeg"] : [".jpg", ".jpeg"] }), ["maxFiles"] : 5, ["onDrop"] : on_drop_20b2deb76b8f31203f8afc1fc0fc2107, ["multiple"] : true, ["id"] : "job_images_upload", ["onDropRejected"] : on_drop_rejected_2fcedbdc0771e7617b4270e2d1ac8cc9 }));



  return (
    jsx(Fragment,{},jsx(RadixThemesBox,{className:"rx-Upload border-2 border-dashed border-slate-700 rounded-xl p-8 hover:border-cyan-500/50 hover:bg-slate-900/50 transition-all cursor-pointer",id:"job_images_upload",ref:ref_job_images_upload,...xdvxrcsn()},jsx("input",{type:"file",...udaxihhe()},),jsx("div",{className:"flex flex-col items-center justify-center text-center"},jsx(LucideImage,{className:"h-10 w-10 text-slate-500 mb-3"},),jsx("p",{className:"text-slate-400 text-sm"},"Drop job images here or click to select"),jsx("p",{className:"text-slate-600 text-xs mt-1"},"Supports JPG, PNG - Images upload automatically"))))
  )
}


function Div_8c0bb61593eb91e1dfc14a149a3d5b65 () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx("div",{className:"mt-3"},jsx("p",{className:"text-sm font-medium text-slate-300 mb-3"},"Uploaded Images"),Array.prototype.map.call(reflex___state____state__app___states___global_state____global_state.client_uploaded_images_rx_state_ ?? [],((filename_rx_state_,index_rx_state_)=>(jsx("div",{className:"flex items-center mt-3 p-3 bg-slate-900 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors",key:index_rx_state_},jsx(LucideFileImage,{className:"h-4 w-4 text-cyan-500 mr-2"},),jsx("span",{className:"text-slate-300 text-sm flex-1"},filename_rx_state_),jsx("button",{className:"ml-2 p-1 hover:bg-red-500/10 rounded transition-colors",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.delete_client_image_by_index", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  }))))},jsx(LucideX,{className:"h-4 w-4 text-red-400 hover:text-red-300"},)))))))
  )
}


function Fragment_8a49e0a96f4b014e4efd180e3e6463df () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)



  return (
    jsx(Fragment,{},((reflex___state____state__app___states___global_state____global_state.client_uploaded_images_rx_state_.length > 0)?(jsx(Fragment,{},jsx(Div_8c0bb61593eb91e1dfc14a149a3d5b65,{},))):(jsx(Fragment,{},))))
  )
}


function Button_3c4e4a3ba5bc63c2b6ca8d354b4ac029 () {
  const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_4a40754333acd683a7a80b8369df8894 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.create_job", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx("button",{className:"flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold py-3 px-8 rounded-xl hover:shadow-lg hover:shadow-cyan-500/20 transition-all active:scale-95 w-full md:w-auto",onClick:on_click_4a40754333acd683a7a80b8369df8894},jsx("span",{},"Create Job"),jsx(LucideArrowRight,{className:"w-4 h-4 ml-2"},))
  )
}


function Comp_483fc185dd453fc86c8f474e5fae19fb () {
  const ref_proof_upload = useRef(null); refs["ref_proof_upload"] = ref_proof_upload;
const [addEvents, connectErrors] = useContext(EventLoopContext);
const [filesById, setFilesById] = useContext(UploadFilesContext);
const on_drop_5929b05c6a51dcd3e556eb6e560ac793 = useCallback(e => setFilesById(filesById => {
    const updatedFilesById = Object.assign({}, filesById);
    updatedFilesById["proof_upload"] = e;
    return updatedFilesById;
  })
    , [addEvents, ReflexEvent, filesById, setFilesById])
const on_drop_rejected_51f7597a906ee6a527ceb347e5723946 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("_call_function", ({ ["function"] : (() => (refs['__toast']?.["error"]("", ({ ["title"] : "Files not Accepted", ["description"] : _ev_0.map(((dmioulfl) => (dmioulfl?.["file"]?.["path"]+": "+dmioulfl?.["errors"].map(((lgviwvuc) => lgviwvuc?.["message"])).join(", ")))).join("\n\n"), ["closeButton"] : true, ["style"] : ({ ["whiteSpace"] : "pre-line" }) })))), ["callback"] : null }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const { getRootProps: zbxordmc, getInputProps: dcmdllti, isDragActive: rjutlsgw} = useDropzone(({ ["accept"] : ({ ["image/png"] : [".png"], ["image/jpeg"] : [".jpg", ".jpeg"] }), ["maxFiles"] : 1, ["multiple"] : true, ["id"] : "proof_upload", ["onDrop"] : on_drop_5929b05c6a51dcd3e556eb6e560ac793, ["onDropRejected"] : on_drop_rejected_51f7597a906ee6a527ceb347e5723946 }));



  return (
    jsx(Fragment,{},jsx(RadixThemesBox,{className:"rx-Upload border-2 border-dashed border-slate-700 rounded-xl p-8 hover:border-cyan-500/50 hover:bg-slate-900/50 transition-all cursor-pointer",id:"proof_upload",ref:ref_proof_upload,...zbxordmc()},jsx("input",{type:"file",...dcmdllti()},),jsx("div",{className:"flex flex-col items-center justify-center text-center"},jsx(LucideCamera,{className:"h-10 w-10 text-slate-500 mb-3"},),jsx("p",{className:"text-slate-400 text-sm"},"Drop image proof here or click to select"),jsx("p",{className:"text-slate-600 text-xs mt-1"},"Supports JPG, PNG"))))
  )
}


function Div_bab028bf021eb4874a66e0a72a59d44f () {
  const [filesById, setFilesById] = useContext(UploadFilesContext);



  return (
    jsx("div",{},Array.prototype.map.call((filesById["proof_upload"] ? filesById["proof_upload"].map((f) => f.name) : []) ?? [],((file_rx_state_,index_390f0bf486c112b066d9260cf7f862cd)=>(jsx("div",{className:"flex items-center mt-3 p-2 bg-slate-900 rounded-lg border border-slate-800",key:index_390f0bf486c112b066d9260cf7f862cd},jsx(LucideFileImage,{className:"h-4 w-4 text-cyan-500 mr-2"},),jsx("span",{className:"text-slate-300 text-sm"},file_rx_state_))))))
  )
}


function Button_39b882c8d8fae791f510087695879dee () {
  const [filesById, setFilesById] = useContext(UploadFilesContext);
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_90b7f891c9c1b1c534d9009cb1133763 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.handle_upload", ({ ["files"] : filesById?.["proof_upload"], ["upload_id"] : "proof_upload", ["extra_headers"] : ({  }) }), ({  }), "uploadFiles"))], [_e], ({  })))), [addEvents, ReflexEvent, filesById, setFilesById])

  return (
    jsx("button",{className:"text-sm text-cyan-400 hover:text-cyan-300 font-medium px-4 py-2 rounded-lg hover:bg-cyan-500/10 transition-colors",onClick:on_click_90b7f891c9c1b1c534d9009cb1133763},"Upload Image")
  )
}


function Fragment_e8fa852966dde4a67ccce09cfdea7ca3 () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__app___states___global_state____global_state.uploaded_image_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(jsx(Fragment,{},jsx("div",{className:"flex items-center"},jsx(LucideCheckCheck,{className:"h-5 w-5 text-green-500 mr-2"},),jsx("span",{className:"text-green-500 text-sm font-medium"},"Proof Uploaded")))):(jsx(Fragment,{},jsx("div",{},)))))
  )
}


function Button_7ec8b97f819bd24d475fa1d217a07368 () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)



  return (
    jsx("button",{className:"group flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold py-3 px-8 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed enabled:hover:shadow-lg enabled:hover:shadow-cyan-500/20 transition-all enabled:active:scale-95 w-full md:w-auto",disabled:(reflex___state____state__app___states___global_state____global_state.uploaded_image_rx_state_?.valueOf?.() === ""?.valueOf?.())},jsx("span",{},"Verify Work & Claim"),jsx(LucideArrowRight,{className:"w-4 h-4 ml-2 group-enabled:group-hover:translate-x-1 transition-transform"},))
  )
}


function Fragment_c2de1f4def2caaca86090914165e50ed () {
  const reflex___state____state__app___states___global_state____global_state = useContext(StateContexts.reflex___state____state__app___states___global_state____global_state)



  return (
    jsx(Fragment,{},(reflex___state____state__app___states___global_state____global_state.user_mode_rx_state_?(jsx(Fragment,{},jsx("div",{className:"animate-in fade-in duration-500"},jsx("div",{className:"mb-10"},jsx("h2",{className:"text-3xl font-bold text-white mb-2"},"Create New Job"),jsx("p",{className:"text-slate-400"},"Define the parameters for your new blockchain task.")),jsx("div",{className:"bg-slate-950/50 rounded-3xl p-8 border border-slate-800"},jsx("div",{className:"mb-6"},jsx("label",{className:"block text-sm font-medium text-slate-300 mb-2"},"Job Description"),jsx(Textarea_26812b47176d76f011cab4809bd18a48,{},)),jsx("div",{className:"mb-6"},jsx("label",{className:"block text-sm font-medium text-slate-300 mb-3"},"Job Images (Optional)"),jsx(Comp_cd734d163e48637b3f590d12c95f5cd7,{},),jsx(Fragment_8a49e0a96f4b014e4efd180e3e6463df,{},)),jsx("div",{className:"flex justify-end"},jsx(Button_3c4e4a3ba5bc63c2b6ca8d354b4ac029,{},)))))):(jsx(Fragment,{},jsx("div",{className:"animate-in fade-in duration-500"},jsx("div",{className:"mb-10"},jsx("h2",{className:"text-3xl font-bold text-white mb-2"},"Welcome Back"),jsx("p",{className:"text-slate-400"},"Manage your blockchain gigs securely and efficiently.")),jsx("div",{className:"grid grid-cols-1 md:grid-cols-3 gap-6 mb-10"},jsx("div",{},jsx("div",{className:"p-6 rounded-2xl bg-slate-800/40 border border-slate-700 hover:border-cyan-500/50 transition-colors cursor-default"},jsx(LucideActivity,{className:"h-6 w-6 text-cyan-400 mb-4"},),jsx("h3",{className:"text-lg font-semibold text-white mb-1"},"Active Jobs"),jsx("p",{className:"text-sm text-slate-400"},"3 Jobs in progress"))),jsx("div",{},jsx("div",{className:"p-6 rounded-2xl bg-slate-800/40 border border-slate-700 hover:border-purple-500/50 transition-colors cursor-default"},jsx(LucideWallet,{className:"h-6 w-6 text-purple-400 mb-4"},),jsx("h3",{className:"text-lg font-semibold text-white mb-1"},"Total Earnings"),jsx("p",{className:"text-sm text-slate-400"},"12.5 ETH"))),jsx("div",{},jsx("div",{className:"p-6 rounded-2xl bg-slate-800/40 border border-slate-700 hover:border-pink-500/50 transition-colors cursor-default"},jsx(LucideUsers,{className:"h-6 w-6 text-pink-400 mb-4"},),jsx("h3",{className:"text-lg font-semibold text-white mb-1"},"Network Status"),jsx("p",{className:"text-sm text-slate-400"},"Connected to Mainnet")))),jsx("div",{},jsx("h3",{className:"text-xl font-bold text-white mb-6"},"Current Assignment"),jsx("div",{className:"bg-slate-950/50 rounded-3xl p-8 border border-slate-800"},jsx("div",{className:"bg-slate-900/80 p-6 rounded-xl border border-slate-700 mb-8"},jsx("div",{className:"flex justify-between items-start mb-4"},jsx("div",{},jsx("h4",{className:"text-xs font-mono text-cyan-400 mb-1"},"Contract #0x8F...2A"),jsx("h3",{className:"text-lg font-semibold text-white"},"Site Cleanup & Debris Removal")),jsx("span",{className:"px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-500 text-xs font-medium border border-yellow-500/20"},"In Progress")),jsx("div",{className:"text-sm"},jsx("div",{className:"flex items-center mb-2"},jsx(LucideMapPin,{className:"h-4 w-4 text-slate-400 mr-2"},),jsx("span",{className:"text-slate-300"},"123 Main St, Crypto Valley")),jsx("div",{className:"flex items-center"},jsx(LucideFuel,{className:"h-4 w-4 text-purple-400 mr-2"},),jsx("span",{className:"text-slate-300 font-mono"},"Reward: 10 GAS")))),jsx("div",{className:"mb-8"},jsx("label",{className:"block text-sm font-medium text-slate-300 mb-3"},"Submit Proof of Work"),jsx(Comp_483fc185dd453fc86c8f474e5fae19fb,{},),jsx(Div_bab028bf021eb4874a66e0a72a59d44f,{},),jsx("div",{className:"flex justify-end mt-2"},jsx(Button_39b882c8d8fae791f510087695879dee,{},))),jsx("div",{className:"flex flex-col md:flex-row items-center justify-end gap-4 pt-6 border-t border-slate-800"},jsx("div",{className:"flex-1"},jsx(Fragment_e8fa852966dde4a67ccce09cfdea7ca3,{},)),jsx(Button_7ec8b97f819bd24d475fa1d217a07368,{},)))))))))
  )
}


export default function Component() {





  return (
    jsx(Fragment,{},jsx("div",{className:"flex min-h-screen bg-slate-900 font-['Inter']"},jsx("aside",{className:"w-72 h-screen fixed left-0 top-0 flex flex-col bg-slate-950 border-r border-slate-800 shadow-2xl z-50"},jsx("div",{className:"h-20 flex items-center px-6 border-b border-slate-800"},jsx("div",{className:"flex items-center gap-3"},jsx(LucideHexagon,{className:"text-cyan-400 h-8 w-8 animate-pulse"},),jsx("h1",{className:"text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500 tracking-tighter"},"SmartPay"))),jsx("nav",{className:"flex-1 flex flex-col overflow-y-auto"},jsx("div",{className:"py-6"},jsx("p",{className:"text-xs font-bold text-slate-500 px-4 mb-4 tracking-widest"},"MENU"),jsx("div",{className:"flex flex-col gap-2 px-3"},jsx("div",{className:(true ? "flex items-center gap-3 px-4 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 cursor-pointer shadow-[0_0_10px_rgba(34,211,238,0.1)]" : "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800/50 border border-transparent cursor-pointer group transition-all duration-200")},jsx(LucideLayoutDashboard,{className:(true ? "text-cyan-400 h-5 w-5" : "text-slate-400 h-5 w-5")},),jsx("span",{className:(true ? "text-cyan-100 font-medium tracking-wide" : "text-slate-400 font-medium group-hover:text-slate-200 transition-colors")},"Dashboard")),jsx("div",{className:(false ? "flex items-center gap-3 px-4 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 cursor-pointer shadow-[0_0_10px_rgba(34,211,238,0.1)]" : "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800/50 border border-transparent cursor-pointer group transition-all duration-200")},jsx(LucideBriefcase,{className:(false ? "text-cyan-400 h-5 w-5" : "text-slate-400 h-5 w-5")},),jsx("span",{className:(false ? "text-cyan-100 font-medium tracking-wide" : "text-slate-400 font-medium group-hover:text-slate-200 transition-colors")},"My Jobs")),jsx("div",{className:(false ? "flex items-center gap-3 px-4 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 cursor-pointer shadow-[0_0_10px_rgba(34,211,238,0.1)]" : "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800/50 border border-transparent cursor-pointer group transition-all duration-200")},jsx(LucideWallet,{className:(false ? "text-cyan-400 h-5 w-5" : "text-slate-400 h-5 w-5")},),jsx("span",{className:(false ? "text-cyan-100 font-medium tracking-wide" : "text-slate-400 font-medium group-hover:text-slate-200 transition-colors")},"Wallet")),jsx("div",{className:(false ? "flex items-center gap-3 px-4 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 cursor-pointer shadow-[0_0_10px_rgba(34,211,238,0.1)]" : "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800/50 border border-transparent cursor-pointer group transition-all duration-200")},jsx(LucideHistory,{className:(false ? "text-cyan-400 h-5 w-5" : "text-slate-400 h-5 w-5")},),jsx("span",{className:(false ? "text-cyan-100 font-medium tracking-wide" : "text-slate-400 font-medium group-hover:text-slate-200 transition-colors")},"Transaction History")),jsx("div",{className:(false ? "flex items-center gap-3 px-4 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 cursor-pointer shadow-[0_0_10px_rgba(34,211,238,0.1)]" : "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800/50 border border-transparent cursor-pointer group transition-all duration-200")},jsx(LucideSettings,{className:(false ? "text-cyan-400 h-5 w-5" : "text-slate-400 h-5 w-5")},),jsx("span",{className:(false ? "text-cyan-100 font-medium tracking-wide" : "text-slate-400 font-medium group-hover:text-slate-200 transition-colors")},"Settings"))),jsx("div",{className:"my-4 border-t border-slate-800/50 mx-4"},),jsx("div",{className:"pb-4"},jsx("p",{className:"text-xs font-bold text-slate-500 px-4 mb-4 tracking-widest"},"SETTINGS"),jsx("div",{className:"mb-6"},jsx("label",{className:"flex items-center justify-between px-4 py-2 hover:bg-slate-800/30 transition-colors cursor-pointer rounded-lg mx-2"},jsx("span",{className:"text-sm font-medium text-slate-300"},"Worker Mode"),jsx("div",{className:"relative inline-flex items-center cursor-pointer"},jsx(Input_30e8b2c09102647e17e5d18b207b155d,{},),jsx("div",{className:"w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-slate-300 after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600 border border-slate-600"},)))),jsx("div",{},jsx("p",{className:"text-xs font-bold text-slate-500 px-4 mb-2 tracking-widest"},"WALLET CONNECT"),jsx("div",{className:"px-4"},jsx("div",{className:"relative"},jsx(LucideWallet,{className:"absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-cyan-500"},),jsx(Select_82772b3edf0af23a4040bea5c09aaeb0,{},),jsx(LucideChevronDown,{className:"absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none"},)))))),jsx("div",{className:"mt-auto p-4 border-t border-slate-800"},jsx("div",{className:"p-4 rounded-xl bg-slate-800/50 border border-slate-700 backdrop-blur-sm"},jsx("div",{className:"flex items-center gap-3"},jsx(LucideUserPen,{className:"h-10 w-10 text-purple-400"},),jsx("div",{},jsx("p",{className:"text-xs text-slate-400 uppercase font-bold"},"Status"),jsx(P_120831e6cc8fabf0065a61158699a766,{},))))))),jsx("main",{className:"ml-72 min-h-screen flex-1 bg-slate-900 p-8 text-slate-200"},jsx("div",{className:"max-w-7xl mx-auto"},jsx(Fragment_c2de1f4def2caaca86090914165e50ed,{},)))),jsx("title",{},"App | Index"),jsx("meta",{content:"favicon.ico",property:"og:image"},))
  )
}