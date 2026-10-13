## Module <ent_hr_disciplinary_tracking>

#### 13.10.2026
#### Version 18.0.1.0.1
##### FIX

- `views/disciplinary_action_views.xml:183` : l'heritage de la vue
  `hr.employee` portait un marqueur de travail `[REMOVED_BUTTON_BOX_DIV]` a la
  place de l'expression xpath. L'installation du module s'arretait sur
  `ValidationError: Invalid Expression while parsing xpath
  "[REMOVED_BUTTON_BOX_DIV]"` (mesure de la carte t_fb193d82) : le bouton
  Disciplinary Action n'etait jamais pose sur la fiche employe. L'expression
  est retablie : `//div[@name='button_box']`.


#### 15.03.2025
#### Version 18.0.1.0.0
##### ADD
- Initial Commit Enterprise Open HRMS Disciplinary Tracking
